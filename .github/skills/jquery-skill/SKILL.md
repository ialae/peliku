---
name: jquery-skill
description: Best practices for writing jQuery code. Covers jQuery patterns, DOM manipulation, event handling, AJAX, plugin development, performance optimization, and migration strategies. Use this skill whenever writing, reviewing, or refactoring jQuery code.
---

# jQuery — Best Practices

These instructions define how to write clean, maintainable, and performant jQuery code. While vanilla JavaScript is preferred for new projects, these guidelines apply when working with jQuery legacy code or when jQuery is a project requirement.

**Tooling enforces most of this automatically:**

```bash
eslint .              # lint
prettier --check .    # format check
```

---

## 1. Code Organization

### File Structure

```
src/
  js/
    modules/
      auth/
        login.js
        logout.js
      cart/
        cart.js
        cart-ui.js
    components/
      modal.js
      dropdown.js
      tabs.js
    utils/
      ajax.js
      validators.js
      dom-helpers.js
    plugins/
      custom-slider.js
      form-validator.js
    main.js
```

### Module Pattern

Use IIFE (Immediately Invoked Function Expression) to avoid global pollution.

```js
// Good — module pattern
const UserModule = (function($) {
  'use strict';

  // Private variables
  const API_URL = '/api/users';
  let currentUser = null;

  // Private methods
  function formatUserName(user) {
    return `${user.firstName} ${user.lastName}`;
  }

  // Public API
  return {
    init() {
      this.bindEvents();
    },

    bindEvents() {
      $('#login-form').on('submit', this.handleLogin.bind(this));
    },

    handleLogin(e) {
      e.preventDefault();
      // Implementation
    },

    getCurrentUser() {
      return currentUser;
    }
  };
})(jQuery);

// Initialize
$(document).ready(function() {
  UserModule.init();
});

// Bad — global pollution
let currentUser = null;

function handleLogin() {
  // Global function
}

$(document).ready(function() {
  $('#login-form').submit(handleLogin);
});
```

### Namespace Your Code

```js
// Good — namespaced
const MyApp = MyApp || {};

MyApp.Auth = (function($) {
  return {
    login() { /* ... */ },
    logout() { /* ... */ }
  };
})(jQuery);

MyApp.Cart = (function($) {
  return {
    addItem() { /* ... */ },
    removeItem() { /* ... */ }
  };
})(jQuery);

// Usage
MyApp.Auth.login();
MyApp.Cart.addItem(product);
```

---

## 2. jQuery Selectors

### Selector Performance

```js
// Good — cache selectors
const $form = $('#login-form');
const $inputs = $form.find('input');
const $submitBtn = $form.find('button[type="submit"]');

$submitBtn.on('click', function() {
  $inputs.val(''); // Use cached selectors
});

// Bad — repeated selections
$('#login-form button[type="submit"]').on('click', function() {
  $('#login-form input').val(''); // Re-selecting every time
});

// Good — use specific selectors
$('#user-name')           // ID selector (fastest)
$('.btn-primary')         // Class selector
$('button.submit-btn')    // Tag + class (more specific)

// Bad — overly complex or slow selectors
$('div > div > p.text')   // Too specific
$(':visible')             // Pseudo-selectors are slow
$('[data-id]')            // Attribute selectors without tag
```

### Selector Best Practices

```js
// Good — prefix jQuery objects with $
const $modal = $('#modal');
const $closeBtn = $modal.find('.close-btn');

// Good — use find() for descendant search
const $list = $('#todo-list');
const $items = $list.find('.todo-item'); // Better than $('#todo-list .todo-item')

// Good — use children() for direct children
const $menu = $('#main-menu');
const $topLevelItems = $menu.children('li');

// Good — use closest() for ancestor search
const $item = $(this).closest('.todo-item');

// Good — use exists check before operations
const $element = $('#optional-element');
if ($element.length) {
  $element.show();
}
```

### Avoid Universal Selectors

```js
// Bad — universal selector
$('*').hide();
$('div *').addClass('highlight');

// Good — specific selector
$('.content').hide();
$('.content .highlight-target').addClass('highlight');
```

---

## 3. DOM Manipulation

### Creating Elements

```js
// Good — create then manipulate
const $card = $('<div>', {
  class: 'card',
  'data-id': '123'
});

$card.append(
  $('<h3>').text(title),
  $('<p>').text(description),
  $('<img>', { src: imageUrl, alt: title })
);

$('#container').append($card);

// Good — build string then create (for complex HTML)
const html = `
  <div class="card" data-id="123">
    <h3>${$.escapeSelector(title)}</h3>
    <p>${$.escapeSelector(description)}</p>
    <img src="${imageUrl}" alt="${title}">
  </div>
`;
$('#container').append(html);

// Bad — repeated appends
$('#container').append('<div class="card">');
$('#container').append('<h3>' + title + '</h3>');
$('#container').append('<p>' + description + '</p>');
$('#container').append('</div>');
```

### Manipulating Elements

```js
// Good — method chaining
$('#message')
  .text('Processing...')
  .addClass('loading')
  .show()
  .delay(2000)
  .fadeOut();

// Good — batch DOM updates
const $list = $('#user-list');
const fragment = $(document.createDocumentFragment());

users.forEach(user => {
  const $item = $('<li>').text(user.name);
  fragment.append($item);
});

$list.append(fragment); // Single DOM update

// Good — use appropriate methods
$element.text(content);        // Set text (auto-escapes)
$element.html(markup);          // Set HTML
$element.val(inputValue);       // Set form value
$element.attr('href', url);     // Set attribute
$element.data('userId', id);    // Set data attribute
$element.prop('checked', true); // Set property

// Bad — inefficient updates
users.forEach(user => {
  $('#user-list').append(`<li>${user.name}</li>`); // DOM update per iteration
});
```

### Class Manipulation

```js
// Good — class methods
$element.addClass('active');
$element.removeClass('hidden');
$element.toggleClass('expanded');
$element.hasClass('selected');

// Good — multiple classes
$element.addClass('active selected highlighted');
$element.removeClass('inactive disabled');

// Good — conditional classes
$element.toggleClass('visible', isVisible);
$element.toggleClass('error', hasError);

// Bad — direct style manipulation (use classes instead)
$element.css('display', 'none');  // Use addClass('hidden') instead
$element.css('color', 'red');     // Use addClass('error') instead
```

### Removing Elements

```js
// Good — remove element
$element.remove();

// Good — remove and keep data/events for reinsertion
const $element = $('#temp').detach();
// Later...
$('#container').append($element);

// Good — remove children
$container.empty();

// Good — remove specific children
$container.find('.temporary').remove();
```

---

## 4. Event Handling

### Attaching Event Handlers

```js
// Good — use on() for event binding
$('#submit-btn').on('click', handleSubmit);
$('#search').on('input', handleSearch);
$('#form').on('submit', handleFormSubmit);

// Good — event delegation for dynamic elements
$('#todo-list').on('click', '.delete-btn', function(e) {
  e.preventDefault();
  const $item = $(this).closest('.todo-item');
  deleteItem($item.data('id'));
});

// Good — multiple events
$('#input').on('focus blur', function() {
  $(this).toggleClass('focused');
});

// Good — namespaced events
$element.on('click.myPlugin', handler);
$element.off('click.myPlugin'); // Remove only namespaced events

// Bad — direct event methods (deprecated)
$('#btn').click(handler);      // Use .on('click', handler)
$('#input').keyup(handler);    // Use .on('keyup', handler)

// Bad — attaching to each element (use delegation)
$('.delete-btn').each(function() {
  $(this).on('click', deleteHandler);
});
```

### Event Object

```js
// Good — use event object
$('#form').on('submit', function(e) {
  e.preventDefault();        // Prevent default action
  e.stopPropagation();      // Stop event bubbling

  const $form = $(e.target);
  const formData = $form.serialize();
});

// Good — access event properties
$document.on('click', '.item', function(e) {
  console.log(e.type);            // Event type
  console.log(e.target);          // Element that triggered event
  console.log(e.currentTarget);   // Element with the handler
  console.log(e.pageX, e.pageY);  // Mouse position
  console.log(e.which);           // Which mouse button or key
});

// Good — one-time events
$button.one('click', function() {
  // Executes only once, then removes itself
  showWelcomeMessage();
});
```

### Custom Events

```js
// Good — trigger custom events
$element.on('user:login', function(e, userData) {
  console.log('User logged in:', userData);
});

$element.trigger('user:login', { userId: '123', name: 'Alice' });

// Good — custom event with data
$.event.trigger({
  type: 'dataLoaded',
  message: 'Data loaded successfully',
  time: new Date()
});
```

### Unbinding Events

```js
// Good — remove specific handler
$element.off('click', handlerFunction);

// Good — remove all events of a type
$element.off('click');

// Good — remove all events
$element.off();

// Good — remove namespaced events
$element.off('.myNamespace');

// Good — cleanup on removal
function cleanup() {
  $element.off();
  $element.removeData();
  $element.remove();
}
```

---

## 5. AJAX and Async Operations

### AJAX Requests

```js
// Good — $.ajax() with full control
$.ajax({
  url: '/api/users',
  method: 'GET',
  dataType: 'json',
  timeout: 5000,
  success(data) {
    displayUsers(data);
  },
  error(jqXHR, textStatus, errorThrown) {
    console.error('Error:', textStatus, errorThrown);
    showError('Failed to load users');
  },
  complete() {
    hideLoadingSpinner();
  }
});

// Good — shorthand methods
$.get('/api/users')
  .done(function(data) {
    displayUsers(data);
  })
  .fail(function(jqXHR, textStatus) {
    showError('Failed to load users');
  })
  .always(function() {
    hideLoadingSpinner();
  });

// Good — POST with data
$.post('/api/users', {
  name: 'Alice',
  email: 'alice@example.com'
})
  .done(function(response) {
    console.log('User created:', response);
  })
  .fail(function() {
    showError('Failed to create user');
  });

// Good — getJSON for JSON responses
$.getJSON('/api/config')
  .done(function(config) {
    applyConfig(config);
  });
```

### AJAX with Promises

```js
// Good — promise-based AJAX
function fetchUser(id) {
  return $.ajax({
    url: `/api/users/${id}`,
    method: 'GET',
    dataType: 'json'
  });
}

// Usage
fetchUser('123')
  .then(function(user) {
    displayUser(user);
    return fetchUserPosts(user.id);
  })
  .then(function(posts) {
    displayPosts(posts);
  })
  .catch(function(error) {
    showError('Failed to load data');
  });

// Good — multiple parallel requests
$.when(
  $.get('/api/users'),
  $.get('/api/posts'),
  $.get('/api/stats')
)
  .done(function(usersResult, postsResult, statsResult) {
    const users = usersResult[0];
    const posts = postsResult[0];
    const stats = statsResult[0];

    renderDashboard({ users, posts, stats });
  })
  .fail(function() {
    showError('Failed to load dashboard');
  });
```

### AJAX Global Events

```js
// Good — global AJAX event handlers
$(document).ajaxStart(function() {
  $('#loading-indicator').show();
});

$(document).ajaxStop(function() {
  $('#loading-indicator').hide();
});

$(document).ajaxError(function(event, jqXHR, settings, thrownError) {
  console.error('AJAX Error:', settings.url, thrownError);
});

// Good — configure defaults
$.ajaxSetup({
  timeout: 10000,
  headers: {
    'X-CSRF-Token': $('meta[name="csrf-token"]').attr('content')
  }
});
```

### Form Serialization

```js
// Good — serialize form data
const formData = $('#user-form').serialize();
// "name=Alice&email=alice%40example.com"

// Good — serialize as array
const formArray = $('#user-form').serializeArray();
// [{ name: "name", value: "Alice" }, { name: "email", value: "alice@example.com" }]

// Good — convert to object
const formObject = $('#user-form').serializeArray().reduce((obj, item) => {
  obj[item.name] = item.value;
  return obj;
}, {});

// Good — submit form via AJAX
$('#user-form').on('submit', function(e) {
  e.preventDefault();

  $.ajax({
    url: $(this).attr('action'),
    method: 'POST',
    data: $(this).serialize(),
    success(response) {
      showSuccess('Form submitted successfully');
    }
  });
});
```

---

## 6. Effects and Animations

### Basic Effects

```js
// Good — basic show/hide
$element.show();
$element.hide();
$element.toggle();

// Good — with duration
$element.show(400);           // 400ms
$element.hide('slow');        // Predefined duration
$element.toggle('fast');

// Good — with callback
$element.fadeOut(300, function() {
  console.log('Animation complete');
  $(this).remove();
});

// Good — fade effects
$element.fadeIn();
$element.fadeOut();
$element.fadeTo(500, 0.5);    // Fade to 50% opacity
$element.fadeToggle();

// Good — slide effects
$element.slideDown();
$element.slideUp();
$element.slideToggle();
```

### Custom Animations

```js
// Good — animate() for custom effects
$element.animate({
  opacity: 0.5,
  left: '+=50px',
  height: 'toggle'
}, {
  duration: 1000,
  easing: 'swing',
  complete() {
    console.log('Animation complete');
  }
});

// Good — queue animations
$element
  .slideUp(300)
  .delay(500)
  .fadeIn(300);

// Good — stop/clear animations
$element.stop();              // Stop current animation
$element.stop(true);          // Stop and clear queue
$element.stop(true, true);    // Stop, clear queue, jump to end
$element.finish();            // Jump to end immediately
```

### Performance Considerations

```js
// Good — use CSS transitions/animations for better performance
// CSS: .fade { transition: opacity 0.3s; }
$element.addClass('fade').css('opacity', 0);

// Bad — animating many elements individually
$('.items').each(function() {
  $(this).animate({ opacity: 0.5 }, 1000);
});

// Better — batch or use CSS
$('.items').css('opacity', 0.5); // Instant
// Or use CSS class with transition
```

---

## 7. Utilities

### Iterating

```js
// Good — $.each() for objects
$.each(user, function(key, value) {
  console.log(key + ':', value);
});

// Good — .each() for jQuery collections
$('.items').each(function(index, element) {
  const $item = $(element);
  $item.data('index', index);
});

// Good — native forEach when jQuery not needed
const items = $('.items').get(); // Convert to array
items.forEach((element, index) => {
  // Native forEach
});

// Good — $.map() for transformation
const ids = $.map(users, function(user) {
  return user.id;
});

// Good — $.grep() for filtering
const activeUsers = $.grep(users, function(user) {
  return user.isActive;
});
```

### Type Checking

```js
// Good — jQuery type checks
$.isArray([1, 2, 3]);        // true
$.isFunction(myFunc);        // true
$.isNumeric('123');          // true
$.isEmptyObject({});         // true
$.isPlainObject({});         // true

// Good — check if jQuery object is empty
if ($element.length === 0) {
  console.log('Element not found');
}

// Good — check if element exists
if ($('#optional').length) {
  // Element exists
}
```

### Extending Objects

```js
// Good — $.extend() for merging
const defaults = { timeout: 5000, retries: 3 };
const options = { timeout: 10000 };
const config = $.extend({}, defaults, options);
// { timeout: 10000, retries: 3 }

// Good — deep merge
const deepMerged = $.extend(true, {}, obj1, obj2);

// Good — plugin defaults pattern
function MyPlugin(element, options) {
  this.settings = $.extend({}, MyPlugin.defaults, options);
}

MyPlugin.defaults = {
  duration: 300,
  easing: 'swing',
  onComplete: null
};
```

### Other Utilities

```js
// Good — $.trim() for string trimming
const cleaned = $.trim('  text  '); // "text"

// Good — $.param() for query strings
const params = $.param({ name: 'Alice', age: 30 });
// "name=Alice&age=30"

// Good — $.parseJSON() (or native JSON.parse)
const data = $.parseJSON('{"name":"Alice"}');

// Good — $.parseHTML() for safe HTML parsing
const $elements = $.parseHTML('<div>Safe</div>');

// Good — $.contains() for DOM hierarchy
if ($.contains(parent, child)) {
  console.log('Child is inside parent');
}
```

---

## 8. Plugin Development

### Basic Plugin Structure

```js
// Good — plugin pattern
(function($) {
  'use strict';

  $.fn.myPlugin = function(options) {
    // Merge options with defaults
    const settings = $.extend({}, $.fn.myPlugin.defaults, options);

    // Chain-ability
    return this.each(function() {
      const $element = $(this);

      // Plugin logic
      $element.data('myPlugin', new MyPluginClass($element, settings));
    });
  };

  // Default options
  $.fn.myPlugin.defaults = {
    duration: 300,
    easing: 'swing',
    onInit: null,
    onComplete: null
  };

  // Plugin class
  class MyPluginClass {
    constructor($element, settings) {
      this.$element = $element;
      this.settings = settings;
      this.init();
    }

    init() {
      this.bindEvents();
      if (this.settings.onInit) {
        this.settings.onInit.call(this.$element);
      }
    }

    bindEvents() {
      this.$element.on('click.myPlugin', this.handleClick.bind(this));
    }

    handleClick(e) {
      e.preventDefault();
      // Implementation
    }

    destroy() {
      this.$element.off('.myPlugin');
      this.$element.removeData('myPlugin');
    }
  }
})(jQuery);

// Usage
$('.elements').myPlugin({
  duration: 500,
  onComplete() {
    console.log('Plugin initialized');
  }
});
```

### Plugin Best Practices

```js
// Good — protect $ alias
(function($) {
  // $ safely refers to jQuery
})(jQuery);

// Good — enable method calls on plugin
$.fn.myPlugin = function(method, ...args) {
  if (typeof method === 'string') {
    // Method call
    return this.each(function() {
      const instance = $(this).data('myPlugin');
      if (instance && typeof instance[method] === 'function') {
        instance[method](...args);
      }
    });
  }

  // Initialization
  const options = method || {};
  return this.each(function() {
    $(this).data('myPlugin', new MyPluginClass($(this), options));
  });
};

// Usage
$('.elements').myPlugin();                    // Initialize
$('.elements').myPlugin('show');               // Call method
$('.elements').myPlugin('destroy');            // Destroy
```

---

## 9. Performance Optimization

### Selector Optimization

```js
// Good — cache selectors
const $container = $('#container');
const $items = $container.find('.item');

// Good — use ID selectors when possible
$('#unique-id'); // Fastest

// Good — scope searches
$container.find('.item'); // Better than $('.item')

// Bad — don't cache length in loops
for (let i = 0; i < $items.length; i++) { // Recalculates length each iteration
  // ...
}

// Good — cache length
const itemCount = $items.length;
for (let i = 0; i < itemCount; i++) {
  // ...
}
```

### DOM Manipulation Optimization

```js
// Bad — multiple DOM updates
for (let i = 0; i < 100; i++) {
  $list.append(`<li>Item ${i}</li>`);
}

// Good — batch updates
const html = [];
for (let i = 0; i < 100; i++) {
  html.push(`<li>Item ${i}</li>`);
}
$list.append(html.join(''));

// Good — use document fragment
const $fragment = $(document.createDocumentFragment());
for (let i = 0; i < 100; i++) {
  $fragment.append(`<li>Item ${i}</li>`);
}
$list.append($fragment);

// Good — detach during manipulation
const $element = $('#heavy-element').detach();
// Perform many operations
$element.append(/* lots of content */);
$('#container').append($element);
```

### Event Delegation

```js
// Bad — binding to each element
$('.delete-btn').on('click', deleteHandler);

// Good — event delegation
$('#list').on('click', '.delete-btn', deleteHandler);
```

### Avoid Heavy Operations in Loops

```js
// Bad
$items.each(function() {
  const $parent = $(this).parents('.container'); // Expensive
  // ...
});

// Good
const $container = $('.container');
$items.each(function() {
  // Use cached $container
});
```

---

## 10. jQuery with Modern JavaScript

### Use Modern JS Features

```js
// Good — arrow functions
$button.on('click', () => {
  console.log('Clicked');
});

// Good — template literals
const $card = $(`
  <div class="card">
    <h3>${title}</h3>
    <p>${description}</p>
  </div>
`);

// Good — destructuring
$form.on('submit', function(e) {
  e.preventDefault();

  const formData = $(this).serializeArray();
  const { name, email } = formData.reduce((obj, { name, value }) => {
    obj[name] = value;
    return obj;
  }, {});
});

// Good — async/await with jQuery AJAX
async function loadUserData(userId) {
  try {
    const user = await $.get(`/api/users/${userId}`);
    const posts = await $.get(`/api/users/${userId}/posts`);

    return { user, posts };
  } catch (error) {
    console.error('Failed to load data:', error);
    throw error;
  }
}
```

### Migration to Vanilla JS

```js
// jQuery → Vanilla JS equivalents

// Selecting
$('#id')                    // document.querySelector('#id')
$('.class')                 // document.querySelectorAll('.class')
$element.find('.child')     // element.querySelectorAll('.child')

// Classes
$element.addClass('active') // element.classList.add('active')
$element.removeClass('x')   // element.classList.remove('x')
$element.toggleClass('x')   // element.classList.toggle('x')

// Attributes
$element.attr('href')       // element.getAttribute('href')
$element.attr('href', url)  // element.setAttribute('href', url)

// Content
$element.text()             // element.textContent
$element.html()             // element.innerHTML
$element.val()              // element.value

// Events
$element.on('click', fn)    // element.addEventListener('click', fn)
$element.off('click', fn)   // element.removeEventListener('click', fn)

// CSS
$element.css('color')       // getComputedStyle(element).color
$element.show()             // element.style.display = 'block'
$element.hide()             // element.style.display = 'none'

// AJAX
$.ajax()                    // fetch()
$.get()                     // fetch(url).then(r => r.json())
```

---

## 11. Common Pitfalls

### Scope Issues

```js
// Bad — losing context
$buttons.each(function() {
  setTimeout(function() {
    $(this).addClass('active'); // `this` is window, not button
  }, 1000);
});

// Good — preserve context with arrow function
$buttons.each(function() {
  setTimeout(() => {
    $(this).addClass('active'); // Arrow function preserves `this`
  }, 1000);
});

// Good — explicit binding
$buttons.each(function() {
  setTimeout(function() {
    $(this).addClass('active');
  }.bind(this), 1000);
});
```

### Memory Leaks

```js
// Bad — not cleaning up
$element.on('click', handler);
// Element removed but event handler remains

// Good — cleanup
function cleanup() {
  $element.off('click', handler);
  $element.removeData();
  $element.remove();
}

// Good — use namespaced events
$element.on('click.myFeature', handler);
// Later:
$element.off('.myFeature'); // Remove all myFeature events
```

### Chaining Issues

```js
// Bad — breaking the chain
$element
  .fadeIn()
  .text('Hello')
  .each(function() {
    // .each() doesn't return jQuery object in callback
    $(this).addClass('active');
  })
  .css('color', 'red'); // This works on $element, not items from .each()

// Good — understand what each method returns
$element
  .fadeIn()
  .text('Hello')
  .addClass('active')
  .css('color', 'red'); // Chain preserves $element
```

---

## 12. Security

### XSS Prevention

```js
// Bad — direct HTML with user input
const userInput = '<script>alert("XSS")</script>';
$('#output').html(userInput); // Executes script!

// Good — use .text() for user content
$('#output').text(userInput); // Renders as text, safe

// Good — escape HTML before using .html()
function escapeHtml(text) {
  return $('<div>').text(text).html();
}

const safe = escapeHtml(userInput);
$('#output').html(safe);

// Good — validate and sanitize
function sanitizeInput(input) {
  return input.replace(/[<>]/g, '');
}
```

### CSRF Protection

```js
// Good — include CSRF token in AJAX requests
$.ajaxSetup({
  headers: {
    'X-CSRF-Token': $('meta[name="csrf-token"]').attr('content')
  }
});

// Good — per-request token
$.ajax({
  url: '/api/data',
  method: 'POST',
  headers: {
    'X-CSRF-Token': getCSRFToken()
  },
  data: formData
});
```

---

## 13. Testing jQuery Code

### Make Code Testable

```js
// Good — testable structure
const UserModule = (function($) {
  return {
    validateEmail(email) {
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    },

    showError(message) {
      $('#error').text(message).show();
    },

    handleSubmit(e) {
      e.preventDefault();
      const email = $('#email').val();

      if (!this.validateEmail(email)) {
        this.showError('Invalid email');
        return false;
      }

      return true;
    }
  };
})(jQuery);

// Can test validateEmail independently
```

---

## 14. Anti-Patterns — Never Do These

- **Never use deprecated methods**: `.live()`, `.delegate()`, `.bind()`, `.unbind()` — use `.on()` and `.off()`
- **Never pollute global namespace**: Always use IIFE or modules
- **Never use `$(this)` repeatedly**: Cache it — `const $this = $(this);`
- **Never animate with JavaScript when CSS works**: Use CSS transitions/animations
- **Never ignore event object**: Always prevent default and stop propagation when needed
- **Never use inline event handlers**: `<div onclick="...">` — use `.on()`
- **Never select without checking length**: Check `$element.length` before operations
- **Never create jQuery objects in loops**: Cache selections outside loops
- **Never use `$.fn` for non-plugin code**: Reserve for actual plugins
- **Never rely on execution order of `.ready()`**: Make modules independent
- **Never use synchronous AJAX**: Set `async: true` (default)
- **Never concatenate HTML with `+`**: Use template literals or array.join()
- **Never use `document.write()`**: Even with jQuery
- **Never modify jQuery.fn.init**: Extend jQuery correctly
- **Never use `eval()` or `new Function()` with user input**: Major security risk
- **Never use `:visible`, `:hidden` extensively**: They're slow, use classes
- **Never use `.size()`**: Use `.length` property
- **Never chain `.end()` excessively**: Makes code hard to follow
- **Never use `$.parseJSON()`**: Use native `JSON.parse()`
- **Never use jQuery for everything**: Know when vanilla JS is simpler

---

## 15. Modern Alternatives

Consider these vanilla JS alternatives for new projects:

```js
// jQuery is great, but often unnecessary now:

// DOM Selection - native is just as easy
// $('.class') → document.querySelectorAll('.class')

// AJAX - fetch API is native
// $.ajax() → fetch()

// Animations - CSS is faster
// $element.fadeIn() → element.classList.add('fade-in')

// Utilities - ES6+ provides most
// $.map() → Array.map()
// $.each() → Array.forEach()
// $.extend() → Object.assign() or spread operator
```

**When to use jQuery:**
- Legacy codebases
- Extensive plugin ecosystems needed
- Cross-browser support for old browsers (IE8-10)
- Team preference/expertise

**When to avoid jQuery:**
- Modern browsers only (ES6+)
- Performance-critical applications
- Small projects
- Learning modern JavaScript
