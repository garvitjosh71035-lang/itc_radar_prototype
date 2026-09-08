# Start here — v2 replacement package

If you want to replace the currently deployed prototype with this version:

1. Back up the old repository/branch.
2. Replace the repository contents with this package.
3. Commit and push.
4. In Render, make sure the frontend environment variable is:
   `VITE_API_URL=https://<your-backend-service>.onrender.com/api`
5. Trigger a redeploy (or let your connected branch auto-deploy).
6. Test `/health` on the backend and then open the frontend Evidence Console.
7. Run at least `RC-0001`, `N1-TRADER`, `N5-ESTATE`, and `N6-UNRES` to demonstrate both fraud signals and false-positive controls.

The frontend build command remains `cd frontend && npm install && npm run build` and emits `frontend/build`.
