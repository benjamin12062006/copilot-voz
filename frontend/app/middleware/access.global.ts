import { accessRoute } from '../utils/access-route';

export default defineNuxtRouteMiddleware(async (to) => {
  // Older Flow configurations return to /; preserve their callback parameters.
  if (to.path === '/') {
    return navigateTo({ path: '/auth', query: to.query }, { replace: true });
  }
  if (
    import.meta.server ||
    !['/', '/auth', '/account', '/session'].includes(to.path)
  )
    return;
  // SSR and the first client render must show the same loading markup.
  // Session restoration begins only after hydration in the client plugin.
  if (useNuxtApp().isHydrating) return;
  const { state, actions } = useAccess();
  await actions.start();
  const destination = accessRoute(state.value);
  if (to.path !== destination)
    return navigateTo(destination, { replace: true });
});
