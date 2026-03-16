---
name: vanilla-js-testing-skill
description: Best practices for testing vanilla JavaScript code with Jest and Vitest. Covers unit testing, DOM testing, async testing, mocking, browser APIs, test organization, and anti-patterns. Use this skill whenever writing, reviewing, or refactoring JavaScript tests.
---

# Vanilla JavaScript Testing — Best Practices

These instructions define how to write, structure, and maintain tests for vanilla JavaScript code. Examples use Vitest (preferred) or Jest with JSDOM for DOM testing.

**One command runs everything:**

```bash
npm test              # or: npx vitest
```

---

## 1. Test Structure and Organization

### Directory Layout

Test files live next to the code they test.

```
src/
  features/
    auth/
      login.js
      login.test.js
      auth-api.js
      auth-api.test.js
  utils/
    validators.js
    validators.test.js
    http.js
    http.test.js
  components/
    modal.js
    modal.test.js
  test/
    setup.js
    helpers.js
    fixtures/
      users.js
      products.js
```

- Test file name: `<filename>.test.js` or `<filename>.spec.js`
- Shared test utilities go in `test/`
- Mock data/fixtures go in `test/fixtures/`
- Colocate tests with source files

### Test Setup

```js
// test/setup.js
import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/dom";
import { afterEach } from "vitest";

// Clean up DOM after each test
afterEach(() => {
  cleanup();
  document.body.innerHTML = "";
  localStorage.clear();
  sessionStorage.clear();
});

// Mock browser APIs if needed
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
};
```

```js
// vitest.config.js
export default {
  test: {
    environment: "jsdom",
    setupFiles: ["./test/setup.js"],
    globals: true,
    coverage: {
      provider: "v8",
      reporter: ["text", "html", "json-summary"],
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

---

## 2. Test Philosophy

### Arrange-Act-Assert Pattern

Every test follows AAA pattern with blank lines between sections.

```js
import { describe, it, expect } from "vitest";
import { calculateDiscount } from "./pricing.js";

describe("calculateDiscount", () => {
  it("should apply 10% discount for orders over $100", () => {
    // Arrange
    const orderTotal = 150;
    const discountRate = 0.1;

    // Act
    const result = calculateDiscount(orderTotal, discountRate);

    // Assert
    expect(result).toBe(15);
  });
});
```

### Test Naming

Pattern: `should <expected behavior> when <scenario>`

```js
// Good
it("should return true when email contains @ symbol", () => { ... });
it("should throw error when age is negative", () => { ... });
it("should cache result after first calculation", () => { ... });

// Bad
it("validates email", () => { ... });
it("works", () => { ... });
it("test1", () => { ... });
```

### Describe Blocks

Group tests logically by function or feature.

```js
describe("User Validator", () => {
  describe("validateEmail", () => {
    it("should return true for valid email", () => { ... });
    it("should return false when email is missing @ symbol", () => { ... });
    it("should return false when email is empty", () => { ... });
  });

  describe("validateAge", () => {
    it("should return true for age between 0 and 150", () => { ... });
    it("should return false for negative age", () => { ... });
    it("should return false for age over 150", () => { ... });
  });
});
```

---

## 3. Testing Pure Functions

### Basic Assertions

```js
import { describe, it, expect } from "vitest";
import { sum, multiply, divide } from "./math.js";

describe("Math utilities", () => {
  describe("sum", () => {
    it("should add two positive numbers", () => {
      expect(sum(2, 3)).toBe(5);
    });

    it("should handle negative numbers", () => {
      expect(sum(-5, 3)).toBe(-2);
    });

    it("should handle zero", () => {
      expect(sum(0, 5)).toBe(5);
    });
  });

  describe("divide", () => {
    it("should divide two numbers", () => {
      expect(divide(10, 2)).toBe(5);
    });

    it("should throw error when dividing by zero", () => {
      expect(() => divide(10, 0)).toThrow("Cannot divide by zero");
    });
  });
});
```

### Testing Object Returns

```js
import { createUser } from "./user-factory.js";

describe("createUser", () => {
  it("should create user with correct properties", () => {
    const user = createUser("Alice", "alice@example.com");

    expect(user).toEqual({
      name: "Alice",
      email: "alice@example.com",
      role: "user",
      createdAt: expect.any(Date),
    });
  });

  it("should use default role when not specified", () => {
    const user = createUser("Bob", "bob@example.com");

    expect(user.role).toBe("user");
  });
});
```

### Testing Arrays

```js
import { filterActiveUsers, sortByName } from "./user-utils.js";

describe("User utilities", () => {
  it("should filter only active users", () => {
    const users = [
      { name: "Alice", isActive: true },
      { name: "Bob", isActive: false },
      { name: "Charlie", isActive: true },
    ];

    const result = filterActiveUsers(users);

    expect(result).toHaveLength(2);
    expect(result).toEqual([
      { name: "Alice", isActive: true },
      { name: "Charlie", isActive: true },
    ]);
  });

  it("should return empty array when no active users", () => {
    const users = [{ name: "Bob", isActive: false }];

    expect(filterActiveUsers(users)).toEqual([]);
  });
});
```

---

## 4. Testing DOM Manipulation

### Setting Up DOM

```js
import { describe, it, expect, beforeEach } from "vitest";
import { createButton, createCard } from "./components.js";

describe("Component creation", () => {
  beforeEach(() => {
    // Clean slate before each test
    document.body.innerHTML = "";
  });

  it("should create button with correct text", () => {
    const button = createButton("Click me");

    expect(button).toBeInstanceOf(HTMLButtonElement);
    expect(button.textContent).toBe("Click me");
  });

  it("should create card with all elements", () => {
    const card = createCard({
      title: "Test Card",
      description: "Description",
      imageUrl: "/image.jpg",
    });

    expect(card.querySelector("h3").textContent).toBe("Test Card");
    expect(card.querySelector("p").textContent).toBe("Description");
    expect(card.querySelector("img").src).toContain("/image.jpg");
  });
});
```

### Testing DOM Updates

```js
import { toggleClass, updateTextContent } from "./dom-utils.js";

describe("DOM utilities", () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div id="target" class="initial">
        <span id="text">Original</span>
      </div>
    `;
  });

  it("should toggle class on element", () => {
    const element = document.querySelector("#target");

    toggleClass(element, "active");
    expect(element.classList.contains("active")).toBe(true);

    toggleClass(element, "active");
    expect(element.classList.contains("active")).toBe(false);
  });

  it("should update text content", () => {
    const element = document.querySelector("#text");

    updateTextContent(element, "Updated");

    expect(element.textContent).toBe("Updated");
  });
});
```

### Using Testing Library

```js
import { screen, fireEvent } from "@testing-library/dom";
import "@testing-library/jest-dom/vitest";
import { createModal } from "./modal.js";

describe("Modal component", () => {
  it("should render modal with title", () => {
    const modal = createModal({ title: "Confirm Action" });
    document.body.appendChild(modal);

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText("Confirm Action")).toBeInTheDocument();
  });

  it("should call onClose when close button clicked", () => {
    const onClose = vi.fn();
    const modal = createModal({ title: "Test", onClose });
    document.body.appendChild(modal);

    const closeBtn = screen.getByRole("button", { name: /close/i });
    fireEvent.click(closeBtn);

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("should not be visible when closed", () => {
    const modal = createModal({ title: "Test", isOpen: false });
    document.body.appendChild(modal);

    expect(modal).not.toBeVisible();
  });
});
```

---

## 5. Testing Event Handlers

### Click Events

```js
import { handleButtonClick, attachClickHandlers } from "./handlers.js";

describe("Event handlers", () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <button id="btn">Click</button>
      <div id="result"></div>
    `;
  });

  it("should update result when button clicked", () => {
    const button = document.querySelector("#btn");
    const result = document.querySelector("#result");

    button.addEventListener("click", () => {
      result.textContent = "Clicked!";
    });

    button.click();

    expect(result.textContent).toBe("Clicked!");
  });

  it("should call callback with event object", () => {
    const callback = vi.fn();
    const button = document.querySelector("#btn");

    button.addEventListener("click", callback);
    button.click();

    expect(callback).toHaveBeenCalledTimes(1);
    expect(callback).toHaveBeenCalledWith(expect.objectContaining({
      type: "click",
      target: button,
    }));
  });
});
```

### Form Events

```js
import { handleFormSubmit } from "./form-handler.js";

describe("Form submission", () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <form id="user-form">
        <input name="name" value="Alice" />
        <input name="email" value="alice@example.com" />
        <button type="submit">Submit</button>
      </form>
    `;
  });

  it("should prevent default form submission", () => {
    const form = document.querySelector("#user-form");
    const event = new Event("submit", { bubbles: true, cancelable: true });
    const preventDefaultSpy = vi.spyOn(event, "preventDefault");

    form.addEventListener("submit", handleFormSubmit);
    form.dispatchEvent(event);

    expect(preventDefaultSpy).toHaveBeenCalled();
  });

  it("should extract form data correctly", () => {
    const form = document.querySelector("#user-form");
    const callback = vi.fn();

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const formData = new FormData(form);
      const data = Object.fromEntries(formData);
      callback(data);
    });

    form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));

    expect(callback).toHaveBeenCalledWith({
      name: "Alice",
      email: "alice@example.com",
    });
  });
});
```

### Input Events

```js
describe("Input handlers", () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <input id="search" type="text" />
      <div id="results"></div>
    `;
  });

  it("should trigger search on input", () => {
    const input = document.querySelector("#search");
    const searchFn = vi.fn();

    input.addEventListener("input", (e) => searchFn(e.target.value));

    input.value = "test query";
    input.dispatchEvent(new Event("input", { bubbles: true }));

    expect(searchFn).toHaveBeenCalledWith("test query");
  });
});
```

### Event Delegation

```js
import { setupEventDelegation } from "./event-delegation.js";

describe("Event delegation", () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <ul id="list">
        <li data-id="1">
          <button class="delete">Delete</button>
        </li>
        <li data-id="2">
          <button class="delete">Delete</button>
        </li>
      </ul>
    `;
  });

  it("should handle clicks on dynamically added items", () => {
    const list = document.querySelector("#list");
    const onDelete = vi.fn();

    list.addEventListener("click", (event) => {
      if (event.target.matches(".delete")) {
        const item = event.target.closest("li");
        onDelete(item.dataset.id);
      }
    });

    // Add new item
    const newItem = document.createElement("li");
    newItem.dataset.id = "3";
    newItem.innerHTML = '<button class="delete">Delete</button>';
    list.appendChild(newItem);

    // Click new item's button
    const deleteBtn = newItem.querySelector(".delete");
    deleteBtn.click();

    expect(onDelete).toHaveBeenCalledWith("3");
  });
});
```

---

## 6. Testing Async Code

### Promises

```js
import { fetchUser, fetchUsers } from "./api.js";

describe("API functions", () => {
  it("should fetch user by id", async () => {
    const user = await fetchUser("123");

    expect(user).toEqual({
      id: "123",
      name: expect.any(String),
      email: expect.any(String),
    });
  });

  it("should throw error when user not found", async () => {
    await expect(fetchUser("invalid")).rejects.toThrow("User not found");
  });

  it("should fetch multiple users", async () => {
    const users = await fetchUsers();

    expect(Array.isArray(users)).toBe(true);
    expect(users.length).toBeGreaterThan(0);
  });
});
```

### Async/Await

```js
import { loadData, processData } from "./async-utils.js";

describe("Async operations", () => {
  it("should load and process data", async () => {
    const data = await loadData();
    const processed = await processData(data);

    expect(processed).toBeDefined();
    expect(processed.status).toBe("complete");
  });

  it("should handle errors gracefully", async () => {
    const invalidData = { invalid: true };

    await expect(processData(invalidData)).rejects.toThrow("Invalid data");
  });
});
```

### Timeouts and Delays

```js
import { debounce, delay } from "./timing.js";
import { vi } from "vitest";

describe("Timing utilities", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("should debounce function calls", () => {
    const fn = vi.fn();
    const debounced = debounce(fn, 1000);

    debounced();
    debounced();
    debounced();

    expect(fn).not.toHaveBeenCalled();

    vi.advanceTimersByTime(1000);

    expect(fn).toHaveBeenCalledTimes(1);
  });

  it("should delay execution", async () => {
    const callback = vi.fn();

    const promise = delay(2000).then(callback);

    expect(callback).not.toHaveBeenCalled();

    vi.advanceTimersByTime(2000);
    await promise;

    expect(callback).toHaveBeenCalled();
  });
});
```

---

## 7. Mocking

### Function Mocks

```js
import { vi } from "vitest";
import { processUser } from "./user-processor.js";

describe("processUser", () => {
  it("should call analytics when user processed", () => {
    const trackEvent = vi.fn();

    processUser({ id: "123", name: "Alice" }, { trackEvent });

    expect(trackEvent).toHaveBeenCalledWith("user_processed", {
      userId: "123",
    });
  });

  it("should call callback with result", () => {
    const callback = vi.fn();

    const result = processUser({ id: "123" }, { onComplete: callback });

    expect(callback).toHaveBeenCalledWith(result);
  });
});
```

### Spying on Methods

```js
describe("Object method spies", () => {
  it("should spy on console.log", () => {
    const logSpy = vi.spyOn(console, "log").mockImplementation(() => {});

    console.log("test message");

    expect(logSpy).toHaveBeenCalledWith("test message");

    logSpy.mockRestore();
  });

  it("should spy on localStorage", () => {
    const setItemSpy = vi.spyOn(Storage.prototype, "setItem");

    localStorage.setItem("key", "value");

    expect(setItemSpy).toHaveBeenCalledWith("key", "value");

    setItemSpy.mockRestore();
  });
});
```

### Module Mocks

```js
// __mocks__/api.js
export const fetchUser = vi.fn().mockResolvedValue({
  id: "123",
  name: "Mock User",
});

export const saveUser = vi.fn().mockResolvedValue({ success: true });

// user-service.test.js
import { vi } from "vitest";
import { getUserProfile } from "./user-service.js";

vi.mock("./api.js");

describe("User Service", () => {
  it("should get user profile", async () => {
    const profile = await getUserProfile("123");

    expect(profile.name).toBe("Mock User");
  });
});
```

### Mocking Fetch

```js
import { vi } from "vitest";

describe("API calls", () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("should fetch user data", async () => {
    const mockUser = { id: "123", name: "Alice" };

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockUser,
    });

    const response = await fetch("/api/users/123");
    const data = await response.json();

    expect(data).toEqual(mockUser);
    expect(fetch).toHaveBeenCalledWith("/api/users/123");
  });

  it("should handle fetch errors", async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      statusText: "Not Found",
    });

    const response = await fetch("/api/users/invalid");

    expect(response.ok).toBe(false);
    expect(response.status).toBe(404);
  });
});
```

---

## 8. Testing Browser APIs

### LocalStorage

```js
import { saveToStorage, loadFromStorage } from "./storage.js";

describe("Storage utilities", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("should save and load data", () => {
    const data = { name: "Alice", age: 30 };

    saveToStorage("user", data);
    const loaded = loadFromStorage("user");

    expect(loaded).toEqual(data);
  });

  it("should return default value when key not found", () => {
    const result = loadFromStorage("missing", { default: true });

    expect(result).toEqual({ default: true });
  });

  it("should handle quota exceeded error", () => {
    const setItemSpy = vi.spyOn(Storage.prototype, "setItem");
    setItemSpy.mockImplementation(() => {
      const error = new Error("QuotaExceededError");
      error.name = "QuotaExceededError";
      throw error;
    });

    expect(() => saveToStorage("key", "value")).toThrow("Storage quota exceeded");

    setItemSpy.mockRestore();
  });
});
```

### IntersectionObserver

```js
import { setupLazyLoading } from "./lazy-load.js";

describe("Lazy loading", () => {
  it("should observe images for lazy loading", () => {
    const observeMock = vi.fn();

    global.IntersectionObserver = vi.fn().mockImplementation((callback) => ({
      observe: observeMock,
      unobserve: vi.fn(),
      disconnect: vi.fn(),
    }));

    document.body.innerHTML = `
      <img class="lazy" data-src="/image1.jpg" />
      <img class="lazy" data-src="/image2.jpg" />
    `;

    setupLazyLoading();

    expect(observeMock).toHaveBeenCalledTimes(2);
  });

  it("should load image when intersecting", () => {
    let observerCallback;

    global.IntersectionObserver = vi.fn().mockImplementation((callback) => {
      observerCallback = callback;
      return {
        observe: vi.fn(),
        unobserve: vi.fn(),
        disconnect: vi.fn(),
      };
    });

    document.body.innerHTML = `<img class="lazy" data-src="/image.jpg" />`;
    const img = document.querySelector("img");

    setupLazyLoading();

    // Trigger intersection
    observerCallback([
      {
        target: img,
        isIntersecting: true,
      },
    ]);

    expect(img.src).toContain("/image.jpg");
    expect(img.classList.contains("lazy")).toBe(false);
  });
});
```

### ResizeObserver

```js
describe("Responsive behavior", () => {
  it("should handle resize events", () => {
    let resizeCallback;
    const observeMock = vi.fn();

    global.ResizeObserver = vi.fn().mockImplementation((callback) => {
      resizeCallback = callback;
      return {
        observe: observeMock,
        unobserve: vi.fn(),
        disconnect: vi.fn(),
      };
    });

    document.body.innerHTML = `<div id="container"></div>`;
    const container = document.querySelector("#container");

    const handler = vi.fn();
    new ResizeObserver(handler).observe(container);

    expect(observeMock).toHaveBeenCalledWith(container);
  });
});
```

### matchMedia

```js
describe("Media queries", () => {
  it("should detect mobile viewport", () => {
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: vi.fn().mockImplementation((query) => ({
        matches: query === "(max-width: 768px)",
        media: query,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
      })),
    });

    const isMobile = window.matchMedia("(max-width: 768px)").matches;
    const isDesktop = window.matchMedia("(min-width: 1024px)").matches;

    expect(isMobile).toBe(true);
    expect(isDesktop).toBe(false);
  });
});
```

---

## 9. Test Coverage

### Running Coverage

```bash
# Generate coverage report
npm test -- --coverage

# View HTML report
open coverage/index.html

# Coverage with threshold enforcement
npm test -- --coverage --coverage.thresholds.lines=80
```

### Coverage Configuration

```js
// vitest.config.js
export default {
  test: {
    coverage: {
      provider: "v8",
      reporter: ["text", "html", "json-summary", "lcov"],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80,
      },
      exclude: [
        "**/*.test.js",
        "**/*.spec.js",
        "**/test/**",
        "**/__mocks__/**",
        "**/node_modules/**",
        "**/*.config.js",
      ],
    },
  },
};
```

### What to Test

**High priority:**
- Business logic and algorithms
- Data validation and transformation
- Error handling paths
- Edge cases and boundary conditions
- User interactions and event handlers

**Lower priority:**
- Third-party library behavior
- Simple getters/setters
- Trivial functions
- Configuration files

### Coverage Goals

- **90%+**: Excellent coverage
- **80-89%**: Good coverage for most projects
- **70-79%**: Acceptable, room for improvement
- **Below 70%**: Needs attention

**Remember:** 100% coverage doesn't mean bug-free code. Focus on meaningful tests.

---

## 10. Testing Patterns

### Testing Factories

```js
// test/fixtures/users.js
export function createMockUser(overrides = {}) {
  return {
    id: "user-123",
    name: "Test User",
    email: "test@example.com",
    role: "user",
    isActive: true,
    createdAt: new Date("2024-01-01"),
    ...overrides,
  };
}

export function createMockAdmin(overrides = {}) {
  return createMockUser({
    role: "admin",
    permissions: ["read", "write", "delete"],
    ...overrides,
  });
}

// In tests
import { createMockUser } from "../test/fixtures/users.js";

it("should process user", () => {
  const user = createMockUser({ email: "custom@example.com" });
  const result = processUser(user);
  expect(result).toBeDefined();
});
```

### Setup and Teardown

```js
describe("User Manager", () => {
  let container;

  beforeEach(() => {
    container = document.createElement("div");
    container.id = "test-container";
    document.body.appendChild(container);
  });

  afterEach(() => {
    container.remove();
    vi.clearAllMocks();
  });

  beforeAll(() => {
    // One-time setup for all tests
    global.API_URL = "https://test-api.example.com";
  });

  afterAll(() => {
    // Clean up after all tests
    delete global.API_URL;
  });

  it("should render user list", () => {
    renderUserList(container);
    expect(container.children.length).toBeGreaterThan(0);
  });
});
```

### Parameterized Tests

```js
describe("Email validation", () => {
  it.each([
    ["valid@example.com", true],
    ["user.name@domain.co.uk", true],
    ["user+tag@example.com", true],
    ["invalid@", false],
    ["@example.com", false],
    ["invalid", false],
    ["", false],
  ])("should return %s for email %s", (email, expected) => {
    expect(validateEmail(email)).toBe(expected);
  });
});

// Or with objects
describe("Age validation", () => {
  it.each([
    { age: 0, expected: true },
    { age: 25, expected: true },
    { age: 150, expected: true },
    { age: -1, expected: false },
    { age: 151, expected: false },
  ])("should validate age $age as $expected", ({ age, expected }) => {
    expect(validateAge(age)).toBe(expected);
  });
});
```

---

## 11. Testing Utilities

### Helper Functions

```js
// test/helpers.js

/**
 * Wait for condition to be true
 */
export async function waitFor(callback, { timeout = 1000, interval = 50 } = {}) {
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    try {
      const result = await callback();
      if (result) return result;
    } catch (error) {
      // Continue waiting
    }
    await new Promise((resolve) => setTimeout(resolve, interval));
  }

  throw new Error("Timeout waiting for condition");
}

/**
 * Wait for element to appear
 */
export async function waitForElement(selector) {
  return waitFor(() => {
    const element = document.querySelector(selector);
    if (element) return element;
    return null;
  });
}

/**
 * Simulate delay
 */
export function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Create DOM element from HTML
 */
export function createElementFromHTML(html) {
  const template = document.createElement("template");
  template.innerHTML = html.trim();
  return template.content.firstElementChild;
}
```

### Custom Matchers

```js
// test/matchers.js
import { expect } from "vitest";

expect.extend({
  toBeWithinRange(received, min, max) {
    const pass = received >= min && received <= max;
    return {
      pass,
      message: () =>
        pass
          ? `Expected ${received} not to be within ${min}-${max}`
          : `Expected ${received} to be within ${min}-${max}`,
    };
  },

  toHaveClass(element, className) {
    const pass = element.classList.contains(className);
    return {
      pass,
      message: () =>
        pass
          ? `Expected element not to have class "${className}"`
          : `Expected element to have class "${className}"`,
    };
  },

  toBeVisible(element) {
    const pass =
      element.offsetWidth > 0 &&
      element.offsetHeight > 0 &&
      window.getComputedStyle(element).visibility !== "hidden";

    return {
      pass,
      message: () =>
        pass
          ? "Expected element not to be visible"
          : "Expected element to be visible",
    };
  },
});

// Usage
it("should show element", () => {
  expect(element).toBeVisible();
  expect(element).toHaveClass("active");
});
```

---

## 12. Integration Testing

### Testing Multiple Components Together

```js
import { renderApp } from "./app.js";
import { screen } from "@testing-library/dom";

describe("Application integration", () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="app"></div>';
  });

  it("should render complete app flow", async () => {
    renderApp();

    // Check header
    expect(screen.getByRole("banner")).toBeInTheDocument();

    // Check navigation
    const nav = screen.getByRole("navigation");
    expect(nav).toBeInTheDocument();

    // Check main content
    expect(screen.getByRole("main")).toBeInTheDocument();
  });

  it("should navigate between pages", async () => {
    renderApp();

    const aboutLink = screen.getByRole("link", { name: /about/i });
    aboutLink.click();

    await waitFor(() => {
      expect(screen.getByText("About Page")).toBeInTheDocument();
    });
  });
});
```

### Testing with Real API (Optional)

```js
describe("User API integration", () => {
  // Only run if TEST_REAL_API=true
  const shouldRunIntegrationTests = process.env.TEST_REAL_API === "true";

  const testIf = (condition) => (condition ? it : it.skip);

  testIf(shouldRunIntegrationTests)("should fetch real user data", async () => {
    const user = await fetchUser("real-user-id");

    expect(user).toHaveProperty("id");
    expect(user).toHaveProperty("name");
    expect(user).toHaveProperty("email");
  });
});
```

---

## 13. Debugging Tests

### Using console.log

```js
it("debugging test", () => {
  const result = calculateTotal(items);

  console.log("Items:", items);
  console.log("Result:", result);
  console.log("DOM:", document.body.innerHTML);

  expect(result).toBe(150);
});
```

### Using debugger

```js
it("step through test", () => {
  const data = { value: 10 };

  debugger; // Execution pauses here when DevTools open

  const result = processData(data);

  expect(result).toBeDefined();
});
```

### Running Single Test

```bash
# Run specific test file
npm test -- user.test.js

# Run tests matching pattern
npm test -- -t "should validate email"

# Run in watch mode
npm test -- --watch

# Run single test file in watch mode
npm test -- --watch user.test.js
```

### Inspecting Failures

```js
it("shows helpful info on failure", () => {
  const expected = { name: "Alice", age: 30 };
  const actual = { name: "Bob", age: 30 };

  // Vitest/Jest shows diff on failure
  expect(actual).toEqual(expected);
  // Output shows:
  // - Expected
  // + Received
  //
  // Object {
  // -  "name": "Alice",
  // +  "name": "Bob",
  //    "age": 30,
  // }
});
```

---

## 14. Performance Testing

### Benchmarking

```js
import { bench, describe } from "vitest";

describe("Performance", () => {
  bench("array map", () => {
    const arr = Array.from({ length: 1000 }, (_, i) => i);
    arr.map((x) => x * 2);
  });

  bench("for loop", () => {
    const arr = Array.from({ length: 1000 }, (_, i) => i);
    const result = [];
    for (let i = 0; i < arr.length; i++) {
      result.push(arr[i] * 2);
    }
  });
});
```

### Testing Performance Requirements

```js
it("should complete within time limit", async () => {
  const startTime = performance.now();

  await expensiveOperation();

  const duration = performance.now() - startTime;

  expect(duration).toBeLessThan(1000); // Must complete in 1 second
});
```

---

## 15. Anti-Patterns — Never Do These

- **Never test implementation details**. Test behavior, not internals.
- **Never write tests that depend on execution order**. Each test must be independent.
- **Never use real API calls in unit tests**. Mock all external dependencies.
- **Never leave console.log in committed tests**. Remove or use proper logging.
- **Never skip or comment out failing tests**. Fix them or delete them.
- **Never test third-party libraries**. Test your usage of them.
- **Never make tests time-dependent without mocking time**. Use fake timers.
- **Never share state between tests**. Clean up after each test.
- **Never test multiple things in one test**. One assertion focus per test.
- **Never use random data without seeding**. Tests must be deterministic.
- **Never mock everything**. Integration tests are valuable.
- **Never write slow tests**. Keep unit tests under 100ms.
- **Never ignore test failures in CI**. All tests must pass.
- **Never test without coverage reporting**. Know what's tested and what's not.
- **Never use snapshots for everything**. Use explicit assertions.
- **Never test getters/setters without logic**. Focus on business logic.
- **Never duplicate test setup**. Use beforeEach or helper functions.
- **Never hardcode test data inline**. Use fixtures and factories.
- **Never test browser-specific behavior without proper setup**. Use jsdom or real browsers.
- **Never ignore async issues**. Properly handle promises and use async/await.

---

## 16. Best Practices Summary

**Do:**
- ✓ Write tests before or alongside code (TDD)
- ✓ Keep tests simple and focused
- ✓ Use descriptive test names
- ✓ Test edge cases and error paths
- ✓ Mock external dependencies
- ✓ Clean up after each test
- ✓ Use factories for test data
- ✓ Aim for 80%+ coverage
- ✓ Run tests in CI/CD
- ✓ Keep tests fast

**Don't:**
- ✗ Test implementation details
- ✗ Share state between tests
- ✗ Ignore failing tests
- ✗ Write slow tests
- ✗ Mock everything
- ✗ Skip edge cases
- ✗ Hardcode test data
- ✗ Leave debug code in tests
- ✗ Test third-party code
- ✗ Depend on test order
