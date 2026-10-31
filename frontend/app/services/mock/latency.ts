/**
 * Espera simulada de red. Respeta `signal` para que cancelar una petición
 * simulada se comporte igual que abortar un fetch real.
 */
export function simulateLatency(ms: number, signal?: AbortSignal) {
  return new Promise<void>((resolve, reject) => {
    if (signal?.aborted) {
      reject(signal.reason);
      return;
    }
    const timer = setTimeout(resolve, ms);
    signal?.addEventListener(
      'abort',
      () => {
        clearTimeout(timer);
        reject(signal.reason);
      },
      { once: true },
    );
  });
}
