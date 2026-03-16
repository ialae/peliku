---
name: jquery-testing-skill
description: Best practices for testing jQuery code with Jest, Vitest, and Jasmine. Covers unit testing, DOM testing, event testing, AJAX mocking, plugin testing, and anti-patterns. Use this skill whenever writing, reviewing, or refactoring jQuery tests.
---

# jQuery Testing — Best Practices

These instructions define how to write, structure, and maintain tests for jQuery code. Examples use Vitest or Jest with JSDOM for DOM testing.

**One command runs everything:**

```bash
npm test              # or: npx vitest
```

---

## 1. Test Setup

### Environment Configuration

```js
// vitest.config.js
export default {
  test: {
    environment: 'jsdom',
    setupFiles: ['./test/setup.js'],
    globals: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80,
      },
    },
  },
};
```

### Test Setup File

```js
// test/setup.js
import { afterEach, beforeEach } from 'vitest';
import $ from 'jquery';

// Make jQuery available globally
global.$ = global.jQuery = $;

// Clean up after each test
afterEach(() => {
  // Clean DOM
  document.body.innerHTML = '';

  // Remove all event handlers
  $(document).off();
  $(window).off();

  // Clear AJAX mock
  if ($.ajax.mockClear) {
    $.ajax.mockClear();
  }
});

beforeEach(() => {
  // Reset any global state
  // Add fixtures if needed
});
```

### Installing Dependencies

```bash
npm install --save-dev vitest jsdom jquery @testing-library/dom
```

---

## 2. Testing DOM Manipulation

### Basic DOM Tests

```js
import { describe, it, expect, beforeEach } from 'vitest';
import $ from 'jquery';
import { createCard } from './card.js';

describe('Card Component', () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="container"></div>';
  });

  it('should create card with title and description', () => {
    const $card = createCard({
      title: 'Test Card',
      description: 'Test description'
    });

    expect($card.find('h3').text()).toBe('Test Card');
    expect($card.find('p').text()).toBe('Test description');
  });

  it('should append card to container', () => {
    const $container = $('#container');
    const $card = createCard({ title: 'Test' });

    $container.append($card);

    expect($container.find('.card').length).toBe(1);
  });

  it('should add correct CSS class', () => {
    const $card = createCard({ title: 'Test', className: 'featured' });

    expect($card.hasClass('card')).toBe(true);
    expect($card.hasClass('featured')).toBe(true);
  });
});
```

### Testing Class Manipulation

```js
import { toggleActive, highlight } from './dom-utils.js';

describe('DOM Utilities', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div id="target" class="item"></div>
    `;
  });

  it('should toggle active class', () => {
    const $element = $('#target');

    toggleActive($element);
    expect($element.hasClass('active')).toBe(true);

    toggleActive($element);
    expect($element.hasClass('active')).toBe(false);
  });

  it('should add highlight class', () => {
    const $element = $('#target');

    highlight($element);

    expect($element.hasClass('highlight')).toBe(true);
  });

  it('should remove multiple classes', () => {
    const $element = $('#target').addClass('foo bar baz');

    $element.removeClass('foo baz');

    expect($element.hasClass('foo')).toBe(false);
    expect($element.hasClass('bar')).toBe(true);
    expect($element.hasClass('baz')).toBe(false);
  });
});
```

### Testing Content Manipulation

```js
describe('Content Updates', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div id="output"></div>
      <input id="input" value="test" />
    `;
  });

  it('should update text content', () => {
    $('#output').text('Hello World');

    expect($('#output').text()).toBe('Hello World');
  });

  it('should update HTML content', () => {
    $('#output').html('<strong>Bold</strong>');

    expect($('#output').find('strong').length).toBe(1);
    expect($('#output').html()).toBe('<strong>Bold</strong>');
  });

  it('should get and set input value', () => {
    expect($('#input').val()).toBe('test');

    $('#input').val('new value');

    expect($('#input').val()).toBe('new value');
  });

  it('should append multiple elements', () => {
    const $output = $('#output');

    $output.append(
      $('<p>').text('First'),
      $('<p>').text('Second')
    );

    expect($output.find('p').length).toBe(2);
    expect($output.find('p').eq(0).text()).toBe('First');
    expect($output.find('p').eq(1).text()).toBe('Second');
  });
});
```

---

## 3. Testing Event Handlers

### Click Events

```js
import { vi } from 'vitest';
import { setupClickHandlers } from './handlers.js';

describe('Click Handlers', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <button id="submit">Submit</button>
      <div id="result"></div>
    `;
  });

  it('should handle button click', () => {
    const callback = vi.fn();

    $('#submit').on('click', callback);
    $('#submit').trigger('click');

    expect(callback).toHaveBeenCalledTimes(1);
  });

  it('should update result on click', () => {
    $('#submit').on('click', function() {
      $('#result').text('Clicked!');
    });

    $('#submit').trigger('click');

    expect($('#result').text()).toBe('Clicked!');
  });

  it('should pass event object to handler', () => {
    const handler = vi.fn();

    $('#submit').on('click', handler);
    $('#submit').trigger('click');

    expect(handler).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'click',
        target: expect.any(Object)
      })
    );
  });
});
```

### Form Events

```js
describe('Form Handlers', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <form id="user-form">
        <input name="name" value="Alice" />
        <input name="email" value="alice@example.com" />
        <button type="submit">Submit</button>
      </form>
    `;
  });

  it('should prevent default form submission', () => {
    const handler = vi.fn((e) => e.preventDefault());

    $('#user-form').on('submit', handler);
    $('#user-form').trigger('submit');

    expect(handler).toHaveBeenCalled();
  });

  it('should serialize form data', () => {
    const serialized = $('#user-form').serialize();

    expect(serialized).toContain('name=Alice');
    expect(serialized).toContain('email=alice%40example.com');
  });

  it('should handle form submission with data', () => {
    const submitHandler = vi.fn(function(e) {
      e.preventDefault();
      const data = $(this).serializeArray();
      return data;
    });

    $('#user-form').on('submit', submitHandler);
    $('#user-form').trigger('submit');

    expect(submitHandler).toHaveBeenCalled();
  });

  it('should validate form before submission', () => {
    const validator = vi.fn(() => false);

    $('#user-form').on('submit', function(e) {
      e.preventDefault();
      if (!validator()) {
        e.stopPropagation();
      }
    });

    $('#user-form').trigger('submit');

    expect(validator).toHaveBeenCalled();
  });
});
```

### Input Events

```js
describe('Input Events', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <input id="search" type="text" />
      <div id="results"></div>
    `;
  });

  it('should trigger on input', () => {
    const handler = vi.fn();

    $('#search').on('input', handler);
    $('#search').val('test').trigger('input');

    expect(handler).toHaveBeenCalled();
  });

  it('should handle keyup event', () => {
    const handler = vi.fn();

    $('#search').on('keyup', handler);

    const event = $.Event('keyup', { keyCode: 13 }); // Enter key
    $('#search').trigger(event);

    expect(handler).toHaveBeenCalledWith(
      expect.objectContaining({ keyCode: 13 })
    );
  });

  it('should debounce input handler', async () => {
    vi.useFakeTimers();
    const handler = vi.fn();

    function debounce(fn, delay) {
      let timeoutId;
      return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn.apply(this, args), delay);
      };
    }

    const debouncedHandler = debounce(handler, 300);

    $('#search').on('input', debouncedHandler);

    $('#search').val('a').trigger('input');
    $('#search').val('ab').trigger('input');
    $('#search').val('abc').trigger('input');

    expect(handler).not.toHaveBeenCalled();

    vi.advanceTimersByTime(300);

    expect(handler).toHaveBeenCalledTimes(1);

    vi.useRealTimers();
  });
});
```

### Event Delegation

```js
describe('Event Delegation', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <ul id="list">
        <li data-id="1"><button class="delete">Delete</button></li>
        <li data-id="2"><button class="delete">Delete</button></li>
      </ul>
    `;
  });

  it('should handle delegated click events', () => {
    const handler = vi.fn();

    $('#list').on('click', '.delete', handler);

    $('.delete').eq(0).trigger('click');

    expect(handler).toHaveBeenCalledTimes(1);
  });

  it('should work with dynamically added elements', () => {
    const handler = vi.fn();

    $('#list').on('click', '.delete', handler);

    // Add new item
    const $newItem = $(`
      <li data-id="3"><button class="delete">Delete</button></li>
    `);
    $('#list').append($newItem);

    // Click new button
    $newItem.find('.delete').trigger('click');

    expect(handler).toHaveBeenCalledTimes(1);
  });

  it('should get correct data from delegated event', () => {
    let deletedId;

    $('#list').on('click', '.delete', function() {
      deletedId = $(this).closest('li').data('id');
    });

    $('.delete').eq(1).trigger('click');

    expect(deletedId).toBe(2);
  });
});
```

### Custom Events

```js
describe('Custom Events', () => {
  it('should trigger and handle custom events', () => {
    const handler = vi.fn();
    const $element = $('<div>');

    $element.on('custom:event', handler);
    $element.trigger('custom:event');

    expect(handler).toHaveBeenCalled();
  });

  it('should pass data with custom events', () => {
    const handler = vi.fn();
    const $element = $('<div>');

    $element.on('user:login', handler);
    $element.trigger('user:login', { userId: '123', name: 'Alice' });

    expect(handler).toHaveBeenCalledWith(
      expect.anything(),
      { userId: '123', name: 'Alice' }
    );
  });

  it('should handle namespaced events', () => {
    const handler1 = vi.fn();
    const handler2 = vi.fn();
    const $element = $('<div>');

    $element.on('click.namespace1', handler1);
    $element.on('click.namespace2', handler2);

    $element.trigger('click');

    expect(handler1).toHaveBeenCalled();
    expect(handler2).toHaveBeenCalled();

    $element.off('.namespace1');
    $element.trigger('click');

    expect(handler1).toHaveBeenCalledTimes(1); // Not called again
    expect(handler2).toHaveBeenCalledTimes(2); // Called again
  });
});
```

---

## 4. Testing AJAX

### Mocking $.ajax

```js
import { vi, beforeEach, afterEach } from 'vitest';

describe('AJAX Requests', () => {
  beforeEach(() => {
    // Mock $.ajax
    vi.spyOn($, 'ajax').mockImplementation(() => {
      const deferred = $.Deferred();
      deferred.resolve({ id: '123', name: 'Test User' });
      return deferred.promise();
    });
  });

  afterEach(() => {
    $.ajax.mockRestore();
  });

  it('should make AJAX request', async () => {
    await $.ajax({
      url: '/api/users/123',
      method: 'GET'
    });

    expect($.ajax).toHaveBeenCalledWith(
      expect.objectContaining({
        url: '/api/users/123',
        method: 'GET'
      })
    );
  });

  it('should handle successful response', async () => {
    const data = await $.ajax({ url: '/api/users/123' });

    expect(data).toEqual({ id: '123', name: 'Test User' });
  });
});
```

### Mocking with Different Responses

```js
describe('AJAX Response Handling', () => {
  it('should handle success response', async () => {
    vi.spyOn($, 'ajax').mockResolvedValue({ success: true, data: [] });

    const result = await $.get('/api/data');

    expect(result.success).toBe(true);

    $.ajax.mockRestore();
  });

  it('should handle error response', async () => {
    const errorResponse = {
      status: 404,
      statusText: 'Not Found',
      responseJSON: { error: 'User not found' }
    };

    vi.spyOn($, 'ajax').mockRejectedValue(errorResponse);

    try {
      await $.get('/api/users/invalid');
    } catch (error) {
      expect(error.status).toBe(404);
      expect(error.responseJSON.error).toBe('User not found');
    }

    $.ajax.mockRestore();
  });

  it('should handle different responses for different calls', async () => {
    const ajaxSpy = vi.spyOn($, 'ajax');

    ajaxSpy
      .mockResolvedValueOnce({ id: 1, name: 'Alice' })
      .mockResolvedValueOnce({ id: 2, name: 'Bob' });

    const user1 = await $.get('/api/users/1');
    const user2 = await $.get('/api/users/2');

    expect(user1.name).toBe('Alice');
    expect(user2.name).toBe('Bob');

    ajaxSpy.mockRestore();
  });
});
```

### Testing AJAX Callbacks

```js
describe('AJAX with Callbacks', () => {
  it('should call success callback', (done) => {
    vi.spyOn($, 'ajax').mockImplementation((options) => {
      setTimeout(() => {
        options.success({ data: 'test' });
        options.complete();
      }, 0);
      return $.Deferred().promise();
    });

    $.ajax({
      url: '/api/test',
      success(data) {
        expect(data).toEqual({ data: 'test' });
      },
      complete() {
        $.ajax.mockRestore();
        done();
      }
    });
  });

  it('should call error callback', (done) => {
    vi.spyOn($, 'ajax').mockImplementation((options) => {
      setTimeout(() => {
        options.error({ status: 500 });
        options.complete();
      }, 0);
      return $.Deferred().promise();
    });

    $.ajax({
      url: '/api/test',
      error(jqXHR) {
        expect(jqXHR.status).toBe(500);
      },
      complete() {
        $.ajax.mockRestore();
        done();
      }
    });
  });
});
```

### Testing with Promises

```js
describe('AJAX Promises', () => {
  it('should resolve promise on success', async () => {
    vi.spyOn($, 'ajax').mockResolvedValue({ id: '123' });

    const data = await $.get('/api/users/123');

    expect(data.id).toBe('123');

    $.ajax.mockRestore();
  });

  it('should chain promises', async () => {
    const ajaxSpy = vi.spyOn($, 'ajax');

    ajaxSpy
      .mockResolvedValueOnce({ userId: '123' })
      .mockResolvedValueOnce({ posts: [] });

    const user = await $.get('/api/session');
    const posts = await $.get(`/api/users/${user.userId}/posts`);

    expect(posts).toEqual({ posts: [] });

    ajaxSpy.mockRestore();
  });

  it('should handle $.when with multiple requests', async () => {
    const ajaxSpy = vi.spyOn($, 'ajax');

    ajaxSpy
      .mockResolvedValueOnce([{ users: [] }])
      .mockResolvedValueOnce([{ posts: [] }])
      .mockResolvedValueOnce([{ stats: {} }]);

    const results = await $.when(
      $.get('/api/users'),
      $.get('/api/posts'),
      $.get('/api/stats')
    );

    expect(results).toBeDefined();

    ajaxSpy.mockRestore();
  });
});
```

---

## 5. Testing Animations and Effects

### Testing Show/Hide

```js
describe('Show/Hide Effects', () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="element" style="display: none;"></div>';
  });

  it('should show element', () => {
    const $element = $('#element');

    $element.show();

    expect($element.css('display')).not.toBe('none');
    expect($element.is(':visible')).toBe(true);
  });

  it('should hide element', () => {
    const $element = $('#element').show(); // Make visible first

    $element.hide();

    expect($element.css('display')).toBe('none');
    expect($element.is(':hidden')).toBe(true);
  });

  it('should toggle visibility', () => {
    const $element = $('#element');

    expect($element.is(':hidden')).toBe(true);

    $element.toggle();
    expect($element.is(':visible')).toBe(true);

    $element.toggle();
    expect($element.is(':hidden')).toBe(true);
  });
});
```

### Testing Animations with Fake Timers

```js
describe('Animations', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    document.body.innerHTML = '<div id="element"></div>';
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should complete animation after duration', () => {
    const callback = vi.fn();
    const $element = $('#element');

    $element.fadeOut(1000, callback);

    expect(callback).not.toHaveBeenCalled();

    vi.advanceTimersByTime(1000);

    expect(callback).toHaveBeenCalled();
  });

  it('should stop animation', () => {
    const $element = $('#element');

    $element.animate({ opacity: 0 }, 1000);
    $element.stop();

    // Animation stopped, won't complete
    vi.advanceTimersByTime(1000);
  });

  it('should finish animation immediately', () => {
    const callback = vi.fn();
    const $element = $('#element');

    $element.fadeOut(1000, callback);
    $element.finish();

    expect(callback).toHaveBeenCalled();
  });
});
```

### Testing Animation Callbacks

```js
describe('Animation Callbacks', () => {
  it('should call callback after fadeIn', (done) => {
    const $element = $('<div>').hide().appendTo('body');

    $element.fadeIn(0, function() {
      expect($(this).is(':visible')).toBe(true);
      done();
    });
  });

  it('should execute queued animations', (done) => {
    const $element = $('<div>').appendTo('body');
    let step = 0;

    $element
      .fadeOut(0, () => { step = 1; })
      .delay(0)
      .fadeIn(0, () => {
        expect(step).toBe(1);
        done();
      });
  });
});
```

---

## 6. Testing jQuery Plugins

### Testing Plugin Initialization

```js
// Assume plugin structure
// $.fn.myPlugin = function(options) { ... }

describe('MyPlugin', () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="target"></div>';
  });

  it('should initialize plugin', () => {
    const $element = $('#target').myPlugin();

    expect($element.data('myPlugin')).toBeDefined();
  });

  it('should merge options with defaults', () => {
    const $element = $('#target').myPlugin({
      customOption: 'custom'
    });

    const plugin = $element.data('myPlugin');

    expect(plugin.settings.customOption).toBe('custom');
  });

  it('should maintain chainability', () => {
    const $element = $('#target')
      .myPlugin()
      .addClass('test');

    expect($element.hasClass('test')).toBe(true);
  });
});
```

### Testing Plugin Methods

```js
describe('Plugin Methods', () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="target"></div>';
    $('#target').myPlugin();
  });

  it('should call plugin method', () => {
    const $element = $('#target');
    const plugin = $element.data('myPlugin');
    const spy = vi.spyOn(plugin, 'show');

    $element.myPlugin('show');

    expect(spy).toHaveBeenCalled();
  });

  it('should pass arguments to plugin method', () => {
    const $element = $('#target');
    const plugin = $element.data('myPlugin');
    const spy = vi.spyOn(plugin, 'setValue');

    $element.myPlugin('setValue', 'test');

    expect(spy).toHaveBeenCalledWith('test');
  });

  it('should destroy plugin', () => {
    const $element = $('#target');

    $element.myPlugin('destroy');

    expect($element.data('myPlugin')).toBeUndefined();
  });
});
```

### Testing Plugin Events

```js
describe('Plugin Events', () => {
  it('should trigger plugin events', () => {
    document.body.innerHTML = '<div id="target"></div>';
    const callback = vi.fn();

    $('#target')
      .on('myPlugin:initialized', callback)
      .myPlugin();

    expect(callback).toHaveBeenCalled();
  });

  it('should pass data with events', () => {
    document.body.innerHTML = '<div id="target"></div>';
    let eventData;

    $('#target')
      .on('myPlugin:change', (e, data) => {
        eventData = data;
      })
      .myPlugin();

    $('#target').myPlugin('setValue', 'test');

    expect(eventData).toEqual({ value: 'test' });
  });
});
```

---

## 7. Testing Utilities

### Testing $.each

```js
describe('$.each', () => {
  it('should iterate over array', () => {
    const items = ['a', 'b', 'c'];
    const results = [];

    $.each(items, (index, value) => {
      results.push(value);
    });

    expect(results).toEqual(['a', 'b', 'c']);
  });

  it('should iterate over object', () => {
    const obj = { name: 'Alice', age: 30 };
    const keys = [];

    $.each(obj, (key, value) => {
      keys.push(key);
    });

    expect(keys).toEqual(['name', 'age']);
  });

  it('should break loop with return false', () => {
    const items = [1, 2, 3, 4, 5];
    const results = [];

    $.each(items, (index, value) => {
      if (value > 3) return false;
      results.push(value);
    });

    expect(results).toEqual([1, 2, 3]);
  });
});
```

### Testing $.map

```js
describe('$.map', () => {
  it('should transform array', () => {
    const numbers = [1, 2, 3];
    const doubled = $.map(numbers, (n) => n * 2);

    expect(doubled).toEqual([2, 4, 6]);
  });

  it('should filter with null return', () => {
    const numbers = [1, 2, 3, 4, 5];
    const evens = $.map(numbers, (n) => (n % 2 === 0 ? n : null));

    expect(evens).toEqual([2, 4]);
  });
});
```

### Testing $.extend

```js
describe('$.extend', () => {
  it('should merge objects', () => {
    const defaults = { a: 1, b: 2 };
    const options = { b: 3, c: 4 };

    const result = $.extend({}, defaults, options);

    expect(result).toEqual({ a: 1, b: 3, c: 4 });
  });

  it('should perform deep merge', () => {
    const obj1 = { a: { x: 1 } };
    const obj2 = { a: { y: 2 } };

    const result = $.extend(true, {}, obj1, obj2);

    expect(result).toEqual({ a: { x: 1, y: 2 } });
  });
});
```

---

## 8. Testing Modules

### Testing Module Pattern

```js
// Module code
const UserModule = (function($) {
  let currentUser = null;

  return {
    setUser(user) {
      currentUser = user;
    },

    getUser() {
      return currentUser;
    },

    isLoggedIn() {
      return currentUser !== null;
    }
  };
})(jQuery);

// Tests
describe('UserModule', () => {
  afterEach(() => {
    UserModule.setUser(null);
  });

  it('should set and get user', () => {
    const user = { id: '123', name: 'Alice' };

    UserModule.setUser(user);

    expect(UserModule.getUser()).toEqual(user);
  });

  it('should check if user is logged in', () => {
    expect(UserModule.isLoggedIn()).toBe(false);

    UserModule.setUser({ id: '123' });

    expect(UserModule.isLoggedIn()).toBe(true);
  });
});
```

### Testing Namespaced Code

```js
const MyApp = MyApp || {};

MyApp.Utils = (function($) {
  return {
    formatCurrency(amount) {
      return '$' + amount.toFixed(2);
    },

    validateEmail(email) {
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }
  };
})(jQuery);

describe('MyApp.Utils', () => {
  it('should format currency', () => {
    expect(MyApp.Utils.formatCurrency(99.5)).toBe('$99.50');
  });

  it('should validate email', () => {
    expect(MyApp.Utils.validateEmail('test@example.com')).toBe(true);
    expect(MyApp.Utils.validateEmail('invalid')).toBe(false);
  });
});
```

---

## 9. Integration Testing

### Testing Complete Workflows

```js
describe('User Login Flow', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <form id="login-form">
        <input name="email" id="email" />
        <input name="password" type="password" id="password" />
        <button type="submit">Login</button>
        <div id="error" style="display: none;"></div>
      </form>
    `;

    vi.spyOn($, 'ajax').mockResolvedValue({ success: true, user: { id: '123' } });
  });

  afterEach(() => {
    $.ajax.mockRestore();
  });

  it('should complete full login flow', async () => {
    const $form = $('#login-form');

    $('#email').val('test@example.com');
    $('#password').val('password123');

    // Simulate form submit
    const submitPromise = new Promise((resolve) => {
      $form.on('submit', function(e) {
        e.preventDefault();

        $.ajax({
          url: '/api/login',
          method: 'POST',
          data: $(this).serialize()
        }).done((response) => {
          resolve(response);
        });
      });
    });

    $form.trigger('submit');

    const result = await submitPromise;

    expect(result.success).toBe(true);
    expect($.ajax).toHaveBeenCalledWith(
      expect.objectContaining({
        url: '/api/login',
        method: 'POST'
      })
    );
  });

  it('should show error on failed login', async () => {
    $.ajax.mockRestore();
    vi.spyOn($, 'ajax').mockRejectedValue({
      responseJSON: { error: 'Invalid credentials' }
    });

    const $form = $('#login-form');

    $('#email').val('test@example.com');
    $('#password').val('wrong');

    const submitPromise = new Promise((resolve) => {
      $form.on('submit', function(e) {
        e.preventDefault();

        $.ajax({
          url: '/api/login',
          method: 'POST',
          data: $(this).serialize()
        })
        .fail((jqXHR) => {
          $('#error').text(jqXHR.responseJSON.error).show();
          resolve();
        });
      });
    });

    $form.trigger('submit');
    await submitPromise;

    expect($('#error').text()).toBe('Invalid credentials');
    expect($('#error').is(':visible')).toBe(true);
  });
});
```

---

## 10. Performance Testing

### Testing Selector Performance

```js
describe('Selector Performance', () => {
  beforeEach(() => {
    const html = [];
    for (let i = 0; i < 1000; i++) {
      html.push(`<div class="item" data-id="${i}">Item ${i}</div>`);
    }
    document.body.innerHTML = `<div id="container">${html.join('')}</div>`;
  });

  it('should use efficient selectors', () => {
    const start = performance.now();

    // Bad: complex selector
    $('.item[data-id="500"]');

    const complexTime = performance.now() - start;

    const start2 = performance.now();

    // Good: scoped search
    $('#container').find('.item').filter('[data-id="500"]');

    const scopedTime = performance.now() - start2;

    // Both should complete quickly, but scoped should be faster
    expect(scopedTime).toBeLessThan(100);
  });
});
```

---

## 11. Common Testing Patterns

### Test Fixtures

```js
// test/fixtures/users.js
export const mockUsers = [
  { id: '1', name: 'Alice', email: 'alice@example.com' },
  { id: '2', name: 'Bob', email: 'bob@example.com' }
];

export function createMockUser(overrides = {}) {
  return {
    id: 'user-123',
    name: 'Test User',
    email: 'test@example.com',
    ...overrides
  };
}

// In tests
import { mockUsers, createMockUser } from './fixtures/users.js';

it('should render users', () => {
  renderUsers(mockUsers);
  expect($('.user-item').length).toBe(2);
});
```

### Setup Helpers

```js
// test/helpers.js
export function setupForm(formHtml) {
  document.body.innerHTML = formHtml;
  return $('#testForm');
}

export function fillForm(data) {
  Object.entries(data).forEach(([name, value]) => {
    $(`[name="${name}"]`).val(value);
  });
}

export function submitForm($form) {
  return new Promise((resolve) => {
    $form.one('submit', (e) => {
      e.preventDefault();
      resolve(new FormData(e.target));
    });
    $form.trigger('submit');
  });
}
```

---

## 12. Anti-Patterns — Never Do These

- **Never test jQuery itself**: Test your code that uses jQuery, not jQuery's functionality
- **Never leave AJAX unmocked**: Always mock $.ajax in unit tests
- **Never rely on timing**: Use fake timers, not actual delays
- **Never test implementation details**: Test behavior, not internal state
- **Never ignore cleanup**: Always unbind events and clear DOM after tests
- **Never use real delays in tests**: Use fake timers or `done()` callback
- **Never share state between tests**: Each test should be independent
- **Never test without mocking AJAX**: Real HTTP calls make tests slow and brittle
- **Never use jQuery methods in assertions when not needed**: Use native assertions
- **Never skip testing edge cases**: Empty states, errors, null values
- **Never test deprecated jQuery methods**: Use modern equivalents
- **Never test plugins without initialization checks**: Always verify plugin was initialized
- **Never forget to restore mocks**: Use `afterEach` to restore spies
- **Never test CSS animations**: Test that classes are applied, not animation
- **Never use brittle selectors in tests**: Use IDs or data attributes
- **Never write slow tests**: Keep tests under 100ms each

---

## 13. Best Practices Summary

**Do:**
- ✓ Mock all AJAX requests
- ✓ Use fake timers for animations/delays
- ✓ Clean up DOM after each test
- ✓ Unbind all event handlers in teardown
- ✓ Test event delegation
- ✓ Test with both jQuery and native methods
- ✓ Use fixtures for test data
- ✓ Test plugin initialization and destruction
- ✓ Test error paths and edge cases
- ✓ Keep tests fast and focused

**Don't:**
- ✗ Test jQuery's implementation
- ✗ Make real HTTP requests
- ✗ Use actual timeouts/delays
- ✗ Share state between tests
- ✗ Test implementation details
- ✗ Ignore memory leaks (unbind events)
- ✗ Skip testing custom events
- ✗ Forget to test chainability
- ✗ Leave debug code in tests
- ✗ Test deprecated methods
