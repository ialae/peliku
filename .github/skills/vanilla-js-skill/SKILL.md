---
name: vanilla-js-skill
description: Best practices for writing vanilla JavaScript code. Covers modern JavaScript features, code organization, DOM manipulation, async patterns, performance, security, and anti-patterns. Use this skill whenever writing, reviewing, or refactoring vanilla JavaScript code.
---

# Vanilla JavaScript — Best Practices

These instructions define how to write clean, maintainable, and modern vanilla JavaScript. All examples use ES2015+ syntax and modern browser APIs.

**Tooling enforces most of this automatically:**

```bash
eslint .              # lint
prettier --check .    # format check
```

---

## 1. Code Organization and Structure

### File Organization

Organize code by feature or domain, not by type.

```
src/
  features/
    auth/
      login.js
      logout.js
      auth-api.js
      auth-storage.js
    cart/
      cart.js
      cart-ui.js
      cart-storage.js
  components/
    modal.js
    dropdown.js
    tabs.js
  utils/
    dom.js
    http.js
    validators.js
    date.js
  constants/
    api-endpoints.js
    app-config.js
  main.js
```

### Module Pattern

Use ES modules for all code organization.

```js
// Good — ES modules
// utils/http.js
export async function fetchJSON(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

export async function postJSON(url, data, options = {}) {
  return fetchJSON(url, {
    method: "POST",
    body: JSON.stringify(data),
    ...options,
  });
}

// main.js
import { fetchJSON, postJSON } from "./utils/http.js";

// Bad — global variables
window.utils = {
  fetchJSON: function() { ... },
  postJSON: function() { ... }
};
```

### File Internal Order

```js
// 1. Imports
import { formatDate } from "./utils/date.js";
import { API_BASE_URL } from "./constants/api-endpoints.js";

// 2. Constants
const MAX_RETRIES = 3;
const TIMEOUT_MS = 5000;

// 3. Module-level variables (if necessary)
let requestCache = new Map();

// 4. Private helper functions
function clearCache() {
  requestCache.clear();
}

// 5. Public API
export async function fetchUser(userId) {
  // Implementation
}

export function invalidateUserCache(userId) {
  // Implementation
}
```

---

## 2. Modern JavaScript Features

### Variables and Constants

Always use `const` by default, `let` when reassignment is needed. Never use `var`.

```js
// Good
const API_KEY = "abc123";
const user = { name: "Alice" };
let counter = 0;

// Bad
var x = 10;
```

### Arrow Functions

Use arrow functions for callbacks and short functions. Use regular functions for methods that need `this` binding.

```js
// Good — arrow function for callbacks
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map((n) => n * 2);
const evens = numbers.filter((n) => n % 2 === 0);

// Good — multiline arrow function
const processUser = (user) => {
  const normalized = normalizeUser(user);
  saveToDatabase(normalized);
  return normalized;
};

// Good — regular function for methods needing `this`
const counter = {
  count: 0,
  increment() {
    this.count++;
  },
};

// Bad — arrow function loses `this` context
const counter = {
  count: 0,
  increment: () => {
    this.count++; // `this` is not the counter object
  },
};
```

### Destructuring

Use destructuring to extract values from objects and arrays.

```js
// Good — object destructuring
const { name, email, role = "user" } = user;

// Good — nested destructuring
const { address: { city, country } } = user;

// Good — array destructuring
const [first, second, ...rest] = items;

// Good — function parameter destructuring
function createUser({ name, email, age = 18 }) {
  return { name, email, age };
}

// Bad — manual extraction
const name = user.name;
const email = user.email;
const role = user.role || "user";
```

### Template Literals

Use template literals for string interpolation and multiline strings.

```js
// Good
const greeting = `Hello, ${user.name}!`;
const html = `
  <div class="card">
    <h2>${title}</h2>
    <p>${description}</p>
  </div>
`;

// Bad
const greeting = "Hello, " + user.name + "!";
const html = "<div class=\"card\">" +
  "<h2>" + title + "</h2>" +
  "<p>" + description + "</p>" +
  "</div>";
```

### Spread and Rest

```js
// Good — spreading arrays
const combined = [...array1, ...array2];
const copy = [...original];

// Good — spreading objects
const updated = { ...original, status: "active" };
const merged = { ...defaults, ...userOptions };

// Good — rest parameters
function sum(...numbers) {
  return numbers.reduce((total, n) => total + n, 0);
}

// Good — rest in destructuring
const { id, createdAt, ...userData } = user;
```

### Optional Chaining and Nullish Coalescing

```js
// Good — optional chaining
const city = user?.address?.city;
const firstItem = items?.[0];
const result = obj.method?.();

// Good — nullish coalescing
const port = config.port ?? 3000;
const name = user.name ?? "Anonymous";

// Bad — manual null checks
const city = user && user.address && user.address.city;
const port = config.port !== null && config.port !== undefined ? config.port : 3000;
```

### Object Shorthand

```js
// Good
const name = "Alice";
const age = 30;

const user = {
  name,
  age,
  greet() {
    return `Hello, I'm ${this.name}`;
  },
};

// Bad
const user = {
  name: name,
  age: age,
  greet: function() {
    return "Hello, I'm " + this.name;
  },
};
```

---

## 3. Functions

### Function Design

Every function should do one thing and do it well.

```js
// Good — single responsibility
function validateEmail(email) {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}

function saveUser(user) {
  return fetch("/api/users", {
    method: "POST",
    body: JSON.stringify(user),
  });
}

// Bad — doing too much
function validateAndSaveUser(email, name) {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!regex.test(email)) return false;

  return fetch("/api/users", {
    method: "POST",
    body: JSON.stringify({ email, name }),
  });
}
```

### Function Parameters

Limit parameters to 3 or fewer. Use an options object for more.

```js
// Good — options object
function createCard({ title, description, imageUrl, onClick, className = "card" }) {
  // Implementation
}

// Bad — too many parameters
function createCard(title, description, imageUrl, onClick, className) {
  // Implementation
}
```

### Default Parameters

```js
// Good
function greet(name = "Guest", greeting = "Hello") {
  return `${greeting}, ${name}!`;
}

// Good — default is result of function call
function processItems(items = getDefaultItems()) {
  return items.map(process);
}

// Bad
function greet(name, greeting) {
  name = name || "Guest";
  greeting = greeting || "Hello";
  return greeting + ", " + name + "!";
}
```

### Pure Functions

Prefer pure functions that don't mutate arguments or depend on external state.

```js
// Good — pure function
function addItem(cart, item) {
  return [...cart, item];
}

// Bad — mutates argument
function addItem(cart, item) {
  cart.push(item);
  return cart;
}

// Good — pure function
function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price, 0);
}

// Bad — depends on external state
let taxRate = 0.1;
function calculateTotal(items) {
  const subtotal = items.reduce((sum, item) => sum + item.price, 0);
  return subtotal * (1 + taxRate);
}
```

### Early Returns

Use early returns to reduce nesting.

```js
// Good — early returns
function processUser(user) {
  if (!user) {
    return null;
  }

  if (!user.isActive) {
    return { error: "User is inactive" };
  }

  if (!user.email) {
    return { error: "Email is required" };
  }

  return processActiveUser(user);
}

// Bad — deeply nested
function processUser(user) {
  if (user) {
    if (user.isActive) {
      if (user.email) {
        return processActiveUser(user);
      } else {
        return { error: "Email is required" };
      }
    } else {
      return { error: "User is inactive" };
    }
  } else {
    return null;
  }
}
```

---

## 4. Async Patterns

### Promises

```js
// Good — clean promise chain
fetch("/api/users")
  .then((response) => response.json())
  .then((users) => {
    displayUsers(users);
  })
  .catch((error) => {
    showError(error.message);
  });

// Good — returning promises
function fetchUser(id) {
  return fetch(`/api/users/${id}`)
    .then((response) => response.json());
}

// Bad — nested promises (callback hell)
fetch("/api/users")
  .then((response) => {
    response.json().then((users) => {
      displayUsers(users);
    });
  });
```

### Async/Await

Prefer async/await over raw promises for readability.

```js
// Good — async/await
async function fetchAndDisplayUser(userId) {
  try {
    const response = await fetch(`/api/users/${userId}`);
    const user = await response.json();
    displayUser(user);
  } catch (error) {
    showError(error.message);
  }
}

// Good — parallel async operations
async function fetchDashboardData() {
  try {
    const [users, posts, stats] = await Promise.all([
      fetchUsers(),
      fetchPosts(),
      fetchStats(),
    ]);

    return { users, posts, stats };
  } catch (error) {
    console.error("Failed to load dashboard:", error);
    throw error;
  }
}

// Bad — sequential when parallel is possible
async function fetchDashboardData() {
  const users = await fetchUsers();
  const posts = await fetchPosts(); // Waits for users unnecessarily
  const stats = await fetchStats(); // Waits for posts unnecessarily
  return { users, posts, stats };
}
```

### Error Handling in Async Code

```js
// Good — proper error handling
async function saveUser(user) {
  try {
    const response = await fetch("/api/users", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(user),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to save user:", error);
    throw error; // Re-throw for caller to handle
  }
}

// Good — handling specific errors
async function fetchWithRetry(url, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url);
      return await response.json();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await delay(1000 * (i + 1)); // Exponential backoff
    }
  }
}
```

### Promise Utilities

```js
// Promise.all — all must succeed
const results = await Promise.all([promise1, promise2, promise3]);

// Promise.allSettled — wait for all, get all results
const results = await Promise.allSettled([promise1, promise2, promise3]);
results.forEach((result) => {
  if (result.status === "fulfilled") {
    console.log(result.value);
  } else {
    console.error(result.reason);
  }
});

// Promise.race — first to complete wins
const fastest = await Promise.race([fetchFromCache(), fetchFromAPI()]);

// Promise.any — first to succeed wins
const firstSuccess = await Promise.any([
  fetchFromServer1(),
  fetchFromServer2(),
  fetchFromServer3(),
]);
```

---

## 5. Objects and Classes

### Object Creation

```js
// Good — object literal
const user = {
  name: "Alice",
  email: "alice@example.com",
  role: "admin",
};

// Good — factory function
function createUser(name, email) {
  return {
    name,
    email,
    role: "user",
    getName() {
      return this.name;
    },
  };
}

// Good — computed property names
const field = "email";
const user = {
  name: "Alice",
  [field]: "alice@example.com",
  [`is${role}`.toUpperCase()]: true,
};
```

### Classes

Use classes for objects that need inheritance or complex behavior.

```js
// Good — class with proper structure
class User {
  static ROLE_ADMIN = "admin";
  static ROLE_USER = "user";

  #password; // Private field

  constructor(name, email, role = User.ROLE_USER) {
    this.name = name;
    this.email = email;
    this.role = role;
    this.#password = null;
  }

  get displayName() {
    return this.name.toUpperCase();
  }

  set password(value) {
    if (value.length < 8) {
      throw new Error("Password must be at least 8 characters");
    }
    this.#password = hashPassword(value);
  }

  isAdmin() {
    return this.role === User.ROLE_ADMIN;
  }

  static fromJSON(json) {
    return new User(json.name, json.email, json.role);
  }
}

// Good — class inheritance
class AdminUser extends User {
  constructor(name, email) {
    super(name, email, User.ROLE_ADMIN);
    this.permissions = [];
  }

  addPermission(permission) {
    this.permissions.push(permission);
  }
}
```

### Object Methods

```js
// Object.keys, values, entries
const user = { name: "Alice", age: 30, role: "admin" };

Object.keys(user); // ["name", "age", "role"]
Object.values(user); // ["Alice", 30, "admin"]
Object.entries(user); // [["name", "Alice"], ["age", 30], ["role", "admin"]]

// Object.assign — shallow copy/merge
const updated = Object.assign({}, user, { age: 31 });

// Object.freeze — prevent modifications
const config = Object.freeze({
  API_URL: "https://api.example.com",
  TIMEOUT: 5000,
});

// Object.fromEntries — convert entries to object
const entries = [["name", "Alice"], ["age", 30]];
const user = Object.fromEntries(entries);

// Object.hasOwn — safer hasOwnProperty
if (Object.hasOwn(user, "name")) {
  console.log(user.name);
}
```

---

## 6. Arrays

### Array Methods

```js
// map — transform each item
const names = users.map((user) => user.name);
const doubled = numbers.map((n) => n * 2);

// filter — select items matching condition
const adults = users.filter((user) => user.age >= 18);
const active = users.filter((user) => user.isActive);

// reduce — accumulate to single value
const total = items.reduce((sum, item) => sum + item.price, 0);
const grouped = items.reduce((acc, item) => {
  const key = item.category;
  acc[key] = acc[key] || [];
  acc[key].push(item);
  return acc;
}, {});

// find — first match
const admin = users.find((user) => user.role === "admin");

// findIndex — index of first match
const index = users.findIndex((user) => user.id === targetId);

// some — at least one matches
const hasAdmin = users.some((user) => user.role === "admin");

// every — all match
const allActive = users.every((user) => user.isActive);

// flat — flatten nested arrays
const nested = [[1, 2], [3, 4], [5]];
const flat = nested.flat(); // [1, 2, 3, 4, 5]

// flatMap — map then flatten
const words = sentences.flatMap((sentence) => sentence.split(" "));
```

### Array Immutability

Never mutate arrays. Use immutable methods.

```js
// Good — immutable operations
const added = [...items, newItem];
const removed = items.filter((item) => item.id !== removeId);
const updated = items.map((item) =>
  item.id === updateId ? { ...item, status: "active" } : item
);

// Bad — mutating operations
items.push(newItem);
items.splice(index, 1);
items[0] = newValue;
```

### Array Utilities

```js
// Unique values
const unique = [...new Set(array)];

// Remove falsy values
const truthy = array.filter(Boolean);

// Sort (non-mutating)
const sorted = [...numbers].sort((a, b) => a - b);
const sortedUsers = [...users].sort((a, b) => a.name.localeCompare(b.name));

// Chunk array
function chunk(array, size) {
  return Array.from({ length: Math.ceil(array.length / size) }, (_, i) =>
    array.slice(i * size, i * size + size)
  );
}

// Range
const range = (start, end) =>
  Array.from({ length: end - start }, (_, i) => start + i);

range(0, 5); // [0, 1, 2, 3, 4]
```

---

## 7. DOM Manipulation

### Selecting Elements

```js
// Good — specific queries
const button = document.querySelector("#submit-btn");
const items = document.querySelectorAll(".item");
const form = document.querySelector("form[name='login']");

// Good — from parent context
const modal = document.querySelector("#modal");
const closeBtn = modal.querySelector(".close-btn");

// Bad — inefficient or outdated
const button = document.getElementById("submit-btn");
const items = document.getElementsByClassName("item");
```

### Creating Elements

```js
// Good — creating elements programmatically
function createCard({ title, description, imageUrl }) {
  const card = document.createElement("div");
  card.className = "card";

  const img = document.createElement("img");
  img.src = imageUrl;
  img.alt = title;

  const titleEl = document.createElement("h3");
  titleEl.textContent = title;

  const descEl = document.createElement("p");
  descEl.textContent = description;

  card.append(img, titleEl, descEl);
  return card;
}

// Good — template strings for complex HTML
function createCard({ title, description, imageUrl }) {
  const template = `
    <div class="card">
      <img src="${escapeHtml(imageUrl)}" alt="${escapeHtml(title)}">
      <h3>${escapeHtml(title)}</h3>
      <p>${escapeHtml(description)}</p>
    </div>
  `;

  const wrapper = document.createElement("div");
  wrapper.innerHTML = template;
  return wrapper.firstElementChild;
}

// Good — HTML template element
const template = document.querySelector("#card-template");
function createCard(data) {
  const clone = template.content.cloneNode(true);
  clone.querySelector(".title").textContent = data.title;
  clone.querySelector(".description").textContent = data.description;
  return clone;
}
```

### Modifying Elements

```js
// Good — class manipulation
element.classList.add("active");
element.classList.remove("hidden");
element.classList.toggle("expanded");
element.classList.contains("selected");

// Good — dataset for data attributes
element.dataset.userId = "123";
const userId = element.dataset.userId;

// Good — attribute manipulation
element.setAttribute("aria-expanded", "true");
element.getAttribute("data-id");
element.removeAttribute("disabled");

// Bad — direct style manipulation (use CSS classes)
element.style.display = "none"; // Use class instead
element.style.color = "red"; // Use class instead
```

### Removing Elements

```js
// Good — remove element
element.remove();

// Good — remove all children
element.replaceChildren();

// Good — remove specific child
parent.removeChild(child);
```

---

## 8. Event Handling

### Adding Event Listeners

```js
// Good — addEventListener
button.addEventListener("click", handleClick);
form.addEventListener("submit", handleSubmit);
input.addEventListener("input", handleInput);

// Good — remove when done
function cleanup() {
  button.removeEventListener("click", handleClick);
}

// Bad — inline event handlers
button.onclick = handleClick; // Can only have one handler

// Bad — HTML event attributes
<button onclick="handleClick()">Click</button>
```

### Event Delegation

Use event delegation for dynamic elements.

```js
// Good — event delegation
const list = document.querySelector("#todo-list");

list.addEventListener("click", (event) => {
  if (event.target.matches(".delete-btn")) {
    const item = event.target.closest(".todo-item");
    deleteTodoItem(item.dataset.id);
  }

  if (event.target.matches(".complete-btn")) {
    const item = event.target.closest(".todo-item");
    toggleComplete(item.dataset.id);
  }
});

// Bad — adding listener to each item
items.forEach((item) => {
  const deleteBtn = item.querySelector(".delete-btn");
  deleteBtn.addEventListener("click", () => deleteTodoItem(item.dataset.id));
});
```

### Event Object

```js
// Good — using event methods
function handleSubmit(event) {
  event.preventDefault(); // Prevent form submission
  event.stopPropagation(); // Stop event bubbling

  const form = event.target;
  const formData = new FormData(form);
  submitData(Object.fromEntries(formData));
}

// Good — accessing event properties
function handleClick(event) {
  console.log(event.type); // "click"
  console.log(event.target); // Element that triggered event
  console.log(event.currentTarget); // Element with listener
  console.log(event.clientX, event.clientY); // Mouse position
}
```

### Custom Events

```js
// Good — dispatching custom events
const event = new CustomEvent("user-login", {
  detail: { userId: "123", timestamp: Date.now() },
  bubbles: true,
});

element.dispatchEvent(event);

// Good — listening for custom events
document.addEventListener("user-login", (event) => {
  console.log("User logged in:", event.detail.userId);
});
```

### Debouncing and Throttling

```js
// Good — debounce (wait until user stops)
function debounce(func, delayMs) {
  let timeoutId;
  return function (...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(this, args), delayMs);
  };
}

const debouncedSearch = debounce((query) => {
  searchAPI(query);
}, 300);

input.addEventListener("input", (e) => debouncedSearch(e.target.value));

// Good — throttle (limit frequency)
function throttle(func, delayMs) {
  let lastRun = 0;
  return function (...args) {
    const now = Date.now();
    if (now - lastRun >= delayMs) {
      func.apply(this, args);
      lastRun = now;
    }
  };
}

const throttledScroll = throttle(() => {
  updateScrollPosition();
}, 100);

window.addEventListener("scroll", throttledScroll);
```

---

## 9. Error Handling

### Try-Catch

```js
// Good — specific error handling
try {
  const user = JSON.parse(userString);
  validateUser(user);
  saveUser(user);
} catch (error) {
  if (error instanceof SyntaxError) {
    showError("Invalid user data format");
  } else if (error instanceof ValidationError) {
    showError(error.message);
  } else {
    showError("An unexpected error occurred");
    console.error(error);
  }
}

// Good — async error handling
async function loadData() {
  try {
    const response = await fetch("/api/data");

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Failed to load data:", error);
    throw error;
  }
}
```

### Custom Errors

```js
// Good — custom error classes
class ValidationError extends Error {
  constructor(field, message) {
    super(message);
    this.name = "ValidationError";
    this.field = field;
  }
}

class NetworkError extends Error {
  constructor(status, message) {
    super(message);
    this.name = "NetworkError";
    this.status = status;
  }
}

// Usage
function validateEmail(email) {
  if (!email.includes("@")) {
    throw new ValidationError("email", "Invalid email format");
  }
}

async function fetchUser(id) {
  const response = await fetch(`/api/users/${id}`);
  if (!response.ok) {
    throw new NetworkError(response.status, "Failed to fetch user");
  }
  return response.json();
}
```

### Global Error Handling

```js
// Good — global error handler
window.addEventListener("error", (event) => {
  console.error("Global error:", event.error);
  logErrorToService(event.error);
  event.preventDefault(); // Prevent default browser error display
});

// Good — unhandled promise rejection handler
window.addEventListener("unhandledrejection", (event) => {
  console.error("Unhandled promise rejection:", event.reason);
  logErrorToService(event.reason);
  event.preventDefault();
});
```

---

## 10. Performance

### Efficient DOM Manipulation

```js
// Bad — multiple reflows
for (let i = 0; i < 1000; i++) {
  const div = document.createElement("div");
  div.textContent = `Item ${i}`;
  container.appendChild(div); // Reflow on each append
}

// Good — batch DOM updates
const fragment = document.createDocumentFragment();
for (let i = 0; i < 1000; i++) {
  const div = document.createElement("div");
  div.textContent = `Item ${i}`;
  fragment.appendChild(div);
}
container.appendChild(fragment); // Single reflow

// Better — innerHTML for many elements
const html = items.map((item) => `<div class="item">${item}</div>`).join("");
container.innerHTML = html;
```

### Lazy Loading

```js
// Good — lazy load images
const imgObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      const img = entry.target;
      img.src = img.dataset.src;
      img.classList.remove("lazy");
      imgObserver.unobserve(img);
    }
  });
});

document.querySelectorAll("img.lazy").forEach((img) => {
  imgObserver.observe(img);
});

// Good — lazy load modules
async function loadFeature() {
  const module = await import("./heavy-feature.js");
  module.initialize();
}

button.addEventListener("click", loadFeature, { once: true });
```

### Memoization

```js
// Good — memoize expensive calculations
function memoize(fn) {
  const cache = new Map();

  return function (...args) {
    const key = JSON.stringify(args);

    if (cache.has(key)) {
      return cache.get(key);
    }

    const result = fn.apply(this, args);
    cache.set(key, result);
    return result;
  };
}

const fibonacci = memoize((n) => {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
});
```

### Web Workers for Heavy Computation

```js
// main.js - offload to worker
const worker = new Worker("worker.js");

worker.postMessage({ numbers: largeArray });

worker.onmessage = (event) => {
  const result = event.data;
  displayResult(result);
};

// worker.js
self.onmessage = (event) => {
  const { numbers } = event.data;
  const result = performExpensiveCalculation(numbers);
  self.postMessage(result);
};
```

---

## 11. Security

### XSS Prevention

```js
// Good — escape user input
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

const userInput = '<script>alert("XSS")</script>';
element.innerHTML = escapeHtml(userInput);

// Good — use textContent for text
element.textContent = userInput; // Automatically safe

// Bad — direct innerHTML with user input
element.innerHTML = userInput; // XSS vulnerability!
```

### Content Security Policy

```js
// Set CSP headers on server
// Content-Security-Policy:
//   default-src 'self';
//   script-src 'self' 'nonce-{random}';
//   style-src 'self' 'nonce-{random}';

// Never use inline event handlers with CSP
// Bad
<button onclick="handleClick()">Click</button>

// Good
<button id="btn">Click</button>
<script nonce="{random}">
  document.getElementById("btn").addEventListener("click", handleClick);
</script>
```

### Input Validation

```js
// Good — validate all inputs
function validateUserInput(data) {
  const errors = {};

  if (!data.email || !isValidEmail(data.email)) {
    errors.email = "Valid email is required";
  }

  if (!data.age || data.age < 0 || data.age > 150) {
    errors.age = "Age must be between 0 and 150";
  }

  if (Object.keys(errors).length > 0) {
    throw new ValidationError("Invalid input", errors);
  }

  return true;
}

// Good — sanitize URLs
function isSafeUrl(url) {
  try {
    const parsed = new URL(url);
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}
```

### Secure Storage

```js
// Good — never store sensitive data in localStorage
// Bad
localStorage.setItem("authToken", token);
localStorage.setItem("password", password);

// Good — use HttpOnly cookies for sensitive data (set server-side)
// Good — sessionStorage for temporary non-sensitive data
sessionStorage.setItem("tempFormData", JSON.stringify(formData));

// Good — clear sensitive data from memory
function logout() {
  sessionStorage.clear();
  // Clear any in-memory sensitive data
  authToken = null;
  userCredentials = null;
}
```

---

## 12. Browser APIs

### Local Storage

```js
// Good — with error handling
function saveToStorage(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    if (error.name === "QuotaExceededError") {
      console.error("Storage quota exceeded");
    }
  }
}

function loadFromStorage(key, defaultValue = null) {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : defaultValue;
  } catch (error) {
    console.error("Failed to parse stored data");
    return defaultValue;
  }
}
```

### Fetch API

```js
// Good — complete fetch implementation
async function apiRequest(url, options = {}) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("Request timeout");
    }
    throw error;
  }
}
```

### FormData

```js
// Good — working with forms
function handleSubmit(event) {
  event.preventDefault();

  const formData = new FormData(event.target);

  // Convert to object
  const data = Object.fromEntries(formData);

  // Or append additional data
  formData.append("timestamp", Date.now());

  // Send as multipart/form-data (for file uploads)
  fetch("/api/upload", {
    method: "POST",
    body: formData, // Don't set Content-Type header
  });
}
```

### IntersectionObserver

```js
// Good — infinite scroll
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        loadMoreItems();
      }
    });
  },
  {
    root: null,
    rootMargin: "100px",
    threshold: 0.1,
  }
);

const sentinel = document.querySelector("#sentinel");
observer.observe(sentinel);
```

### ResizeObserver

```js
// Good — responsive behavior
const resizeObserver = new ResizeObserver((entries) => {
  entries.forEach((entry) => {
    const width = entry.contentRect.width;

    if (width < 768) {
      switchToMobileLayout();
    } else {
      switchToDesktopLayout();
    }
  });
});

resizeObserver.observe(container);
```

---

## 13. Testing and Debugging

### Console Methods

```js
// Log levels
console.log("Info message");
console.warn("Warning message");
console.error("Error message");
console.info("Info message");

// Grouping
console.group("User Details");
console.log("Name:", user.name);
console.log("Email:", user.email);
console.groupEnd();

// Table
console.table(users);

// Time measurement
console.time("operation");
performOperation();
console.timeEnd("operation");

// Assertions
console.assert(value > 0, "Value must be positive");

// Stack trace
console.trace("Execution path");
```

### Debugging

```js
// Breakpoints in code
debugger; // Execution pauses here if DevTools open

// Conditional logging
const DEBUG = true;
function debug(...args) {
  if (DEBUG) {
    console.log(...args);
  }
}
```

---

## 14. Anti-Patterns — Never Do These

- **Never use `var`**. Always use `const` or `let`.
- **Never use `==` or `!=`**. Always use `===` or `!==`.
- **Never use `eval()`**. It's a security risk and performance killer.
- **Never use `with`**. It's deprecated and confusing.
- **Never modify built-in prototypes**. `Array.prototype.myMethod = ...` causes conflicts.
- **Never use synchronous XMLHttpRequest**. Use `fetch` or async XHR.
- **Never use `document.write()`**. It's outdated and problematic.
- **Never mutate function parameters**. Create new objects/arrays instead.
- **Never create functions in loops**. Define once, reference many times.
- **Never ignore error handling**. Always handle promises and try-catch blocks.
- **Never mix business logic with DOM manipulation**. Separate concerns.
- **Never use global variables**. Use modules, closures, or proper scoping.
- **Never use `arguments` object**. Use rest parameters `...args`.
- **Never rely on automatic semicolon insertion**. Always use semicolons explicitly.
- **Never use `new Function()`** with user input. It's like `eval()`.
- **Never use `innerHTML` with unsanitized user input**. XSS vulnerability.
- **Never access `__proto__` directly**. Use `Object.getPrototypeOf()`.
- **Never use `for...in` for arrays**. Use `for...of` or array methods.
- **Never leave `console.log` in production code**. Remove or use proper logging.
- **Never use nested callbacks**. Use promises or async/await.
