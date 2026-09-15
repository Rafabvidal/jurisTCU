import { QueryClient } from "@tanstack/vue-query";

// Prevent refetching when navigating between routes by disabling refetch on mount
// and making data stay fresh for a long time.
const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            refetchOnWindowFocus: false,
            refetchOnReconnect: false,
            staleTime: 1000 * 60 * 60 * 24, // 24 horas
        },
    },
});

export default queryClient;