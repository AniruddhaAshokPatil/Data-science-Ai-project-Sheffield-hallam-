# Frontend Issue Alignment

I created this note so I can show exactly how the insurance website work maps back to the open GitHub issues.

## What I am building now

I am treating the insurance website as a real tracked frontend under `src/frontend/src` instead of relying on the older Streamlit-only direction.

The website now has three product-facing areas:

- A public home page
- A user dashboard
- A company fraud dashboard

## How this maps to the issues

| Issue | Status after this frontend work | Evidence |
| --- | --- | --- |
| `#23 Create React Frontend Skeleton` | I can now align this issue with tracked source files | `src/frontend/package.json`, `src/frontend/vite.config.js`, `src/frontend/index.html`, `src/frontend/src/*` |
| `#24 Build Fraud Monitoring Dashboard Components` | I can now align this issue with tracked dashboard views and components | `src/frontend/src/App.jsx`, `src/frontend/src/styles.css`, `src/frontend/src/data/mockData.js` |
| `#25 Connect Frontend to WebSocket Alert Stream` | I am not fully complete yet, but I am now structurally ready for it | The company dashboard already has a live-alert area driven by simulated updates that I can later replace with a WebSocket client |

## Why I am moving beyond Streamlit

I can still use Streamlit for fast model demos, but the issue list clearly expects a website-style frontend.
Because of that, I am using React/Vite as the main tracked frontend direction for the insurance product experience.

## Why I do not need a real insurance company website link

I do not need a live insurer link in order to implement the product structure.
I can build an original interface around the workflow you want:

- public trust-building homepage
- policyholder claim dashboard
- internal company fraud dashboard

If you later want a specific visual inspiration, I can adapt the styling direction without copying another company's product directly.
