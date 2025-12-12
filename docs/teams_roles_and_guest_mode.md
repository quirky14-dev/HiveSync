# teams_roles_and_guest_mode.md
HiveSync — Team Role Recalculation & Guest Mode Specification  

# 1. Purpose

This document defines:
- Required behavior for recalculating team roles after ownership transfer.
- Required constraints and permissions for Guest Mode.
- Backend rules for write-restriction enforcement.
- Limits on Free-tier users joining teams.

The rules in this document are authoritative and must be followed exactly in backend code and UI enforcement.

---

# 2. Team Roles

Valid roles are:

- `owner`
- `admin`
- `member`
- `guest`

These roles determine capabilities inside a team.

## 2.1 Role Definitions

### owner
- Exactly one per team.
- Full control over team membership and settings.
- Inherited automatically upon transfer events.

### admin
- Elevated rights to manage members except the owner.
- Cannot delete the team.

### member
- Standard contributor.
- Can perform actions permitted by their personal tier and team tier.

### guest
- Assigned to Free-tier users joining a team.
- Read-only role.

---

# 3. Ownership Transfer — Recalculation Rules (TODO #8)

After any ownership transfer event, a recalculation pass **must** enforce the following invariants.

## 3.1 Required Invariants

1. **Exactly one owner**
   - If multiple owners are detected, choose the most recently active user as `owner`.
   - All other users previously marked as owners become `admin`.

2. **Old owner becomes admin**
   - If the previous owner remains in the team, they must become `admin`.

3. **No missing owner**
   - If the system cannot determine a new owner, the team is marked for deletion or escalation according to admin policy.

4. **Guest roles preserved**
   - No guest user may be upgraded automatically during recalculation.
   - Guest status remains unless explicitly changed by admin action.

5. **Free-tier users inheriting ownership**
   - Allowed only temporarily.
   - Must receive an upgrade-required flag.
   - Their ability to exceed Free-tier limits is blocked until upgraded.

## 3.2 When Role Recalculation Must Run

- After user-initiated account deletion.
- After dormant auto-deletion.
- After explicit ownership transfer.
- After mass role changes initiated by admin.

---

# 4. Guest Mode — Global Rules (TODO #9)

## 4.1 Free-tier Team Membership Rule

- A Free-tier user may join **exactly one** team.
- Backend must reject any attempt to join a second team with:
  - HTTP 403 error
  - Message: `"Free accounts can join only one team."`

## 4.2 Guest Role Assignment

- Free-tier users joining a team are assigned `guest`.
- Pro and Premium users may join as `member` or `admin`; they are not automatically `guest`.

## 4.3 Guest Permissions — Read-Only Mode

Guests **cannot**:

- Generate architecture maps
- Generate previews
- Edit project files
- Run AI jobs
- Run diff jobs (component or worker-based)
- Trigger write operations of any kind on team projects

Guests **can**:

- View architecture maps
- View previews
- View files in read-only mode
- View notifications
- View tasks
- View basic diffs (static, non-worker, if permitted)

---

# 5. Backend Enforcement Rules

A backend enforcement function must exist:

```

enforce_guest_mode(user_id, team_id)

```

The function determines whether the user:

- Is a guest in the given team
- Is a Free-tier user
- Must be denied write operations

## 5.1 Required Behavior

If:

- role == `guest`, **and**
- user tier == `free`

then:

```

can_write = false

```

Any write-required endpoint must block the action and return HTTP 403 with a consistent message:

```

"Guest accounts on the Free tier are read-only for team projects."

```

## 5.2 Where Enforcement Must Occur

All write-type actions must call or incorporate `enforce_guest_mode`, including:

- `/architecture/map/generate`
- `/preview/send`
- `/ai/*` (docs, rename, summary, refactor)
- `/diff/file` (worker mode)
- `/diff/component`
- Any file-write or refactor endpoints

Backend enforcement must occur before any worker enqueue.

---

# 6. UI Integration Requirements

The UI must detect guest mode via backend data and:

- Display a **“Guest — Read-Only”** badge in team contexts.
- Disable buttons for:
  - Map generation  
  - Preview generation  
  - AI/refactor/diff jobs  
  - Editing features  
- Display upgrade prompts if a guest attempts restricted actions.

## 6.1 Upgrade Prompt Text

A consistent modal must be displayed:

```

This action is not available to Guest users on the Free tier.
Upgrade your HiveSync account to unlock editing, map generation, previews, and AI features.

```

---

# 7. Summary of Mandatory Guarantees

- Free-tier users join exactly one team.
- Free-tier team members are always `guest`.
- Guests are read-only.
- Role recalculation ensures exactly one owner and demotes old owners to admin.
- Guest roles are not changed automatically.
- Free-tier users inheriting ownership must be upgrade-restricted.
- Backend and UI must enforce consistent read-only behavior.

---

# End of teams_roles_and_guest_mode.md