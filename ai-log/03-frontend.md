# Session 03 — Frontend: wizard, resume, validation states

---

### D12 — Session bootstrap: single POST-based query · _accepted_
One `useQuery(['session'], POST /sessions)` instead of a bootstrap-mutation + id-keyed GET query. `POST /sessions` is idempotent, so it doubles as create-and-resume; no session id ever held in React state.

### D13 — Design handoff: `INVALID` routing kept direct-to-Details · _accepted_
Design's screen 2d shows `INVALID` as its own intermediate Validate screen before returning to Details. Asked first (`BRIEF.md` doesn't mandate either); kept the existing direct-to-Details-with-banner behavior. 2d's copy stays documentation-only.

### D14 — Screens 2b/2c merged into `ReviewStep` · _accepted, not asked first_
Backend has one `VALIDATED` status, no "confirmed to proceed" transition to hang a second screen off of, and 2c's "Back to details" button would `409` (`submit_details` isn't legal from `VALIDATED`). Collapsed into one Review screen; warnings block carries in in per the design README's own note. Followed directly from constraints already fixed elsewhere, so didn't stop to ask.

### D15 — Dev reset: backend endpoint + button, not a script · _accepted_
`POST /dev/reset` (tagged `dev`, separate from the partner-facing API) + a button that only renders in dev builds, over an npm-script alternative. Triggers a full page reload rather than query invalidation, since `DetailsStep`'s form state wouldn't otherwise clear if reset while already on that screen.

### D16 — Component structure: folder-per-component + hook-per-component · _redirected_
Requested: text constants at top of file, one hook per component (`ComponentName/ComponentName.tsx` + `useComponentName.ts`), props wrapped in a local `interface Props`, and `SubmitEvent<HTMLFormElement>` instead of `FormEvent` (confirmed genuinely deprecated in the installed React types). Applied across all 8 components.

### D17 — Frontend conventions pass · _redirected_
Requested in one batch: `@/*` path alias over relative imports, hooks never inline-return (assign to a named const first), enums instead of string-literal union types (moved to per-component `*.constants.ts` files when exported), mapped `Record` objects instead of ternary chains, zero inline `style={{}}` (moved to real CSS classes), and per-component constants files once a component passes ~5 text literals. Applied across every file. One real conflict found, not routed around: the Vite scaffold's `erasableSyntaxOnly` tsconfig flag forbids real TS `enum` declarations outright — disabled it (doesn't affect Vite's actual esbuild-based build, only the type-checker's strictness).
