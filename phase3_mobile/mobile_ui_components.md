# Mobile UI Components

## 1. Overview

The mobile UI is composed of a set of reusable components designed to work across phone and iPad layouts. This document describes the responsibilities and props of core components used in the preview, suggestions, notifications, and code viewing flows.

---

## 2. Core Components

### 2.1 TokenInput

- **Used in**: HomeScreen
- **Purpose**: Capture preview token from the user
- **Props**:
  - `value: string`
  - `onChange(value: string)`
  - `onSubmit()`
  - `errorMessage?: string`
- **Behavior**:
  - Normalizes whitespace
  - Optional input masking/validation feedback

### 2.2 PreviewFrame

- **Used in**: PreviewScreen, iPad left pane
- **Purpose**: Host the React Native / Expo preview runtime
- **Props**:
  - `status: "loading" | "ready" | "error"`
  - `error?: MobileError`
  - `onRetry?()`
- **Behavior**:
  - Displays loading spinners, preview, or error states
  - Provides container for RN root view

### 2.3 SuggestionsList

- **Used in**: SuggestionsScreen, iPad right pane
- **Purpose**: Render AI suggestion cards (docs, explanations, refactors)
- **Props**:
  - `items: Suggestion[]`
  - `onSelect(item: Suggestion)`
- **Behavior**:
  - Virtualized list
  - Tappable items open detail view or scroll CodeViewer

### 2.4 NotificationList

- **Used in**: NotificationsScreen
- **Purpose**: Render events (AI done, preview ready, sync completed)
- **Props**:
  - `items: Notification[]`
  - `onSelect(item: Notification)`
- **Behavior**:
  - Polls backend indirectly via screen/hook
  - Marks items as read when tapped

### 2.5 CodeViewer (iPad)

- **Used in**: iPad split view
- **Purpose**: Syntax-highlighted code rendering
- **Props**:
  - `filePath: string`
  - `content: string`
  - `language: string`
  - `highlightRanges?: { startLine: number; endLine: number }[]`
- **Behavior**:
  - Provides scroll-to-line utilities
  - Uses a lightweight syntax highlighter suitable for large files

---

## 3. Shared Patterns

- All components are built to be theme-aware (light/dark mode if enabled).
- Loading, empty, and error states are standardized:
  - `LoadingSpinner`
  - `EmptyState`
  - `InlineErrorBanner`

---

## 4. Relationship to Other Docs

- `mobile_ipad_layout.md` — describes how components are arranged in split view
- `mobile_error_model.md` — defines `MobileError` interface used in error props
- `mobile_api_usage.md` — describes the data sources for component props
