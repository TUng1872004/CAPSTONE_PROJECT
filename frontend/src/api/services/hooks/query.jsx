import api from "@/api/api";
import { useQuery } from "react-query";

export function useVideos(groupId, sessionId) {
    return useQuery({
        queryKey: ["videos", groupId, sessionId],
        queryFn: async () => {
            const res = await api.get(`/api/user/videos`, {
                params: {
                    session_id: sessionId,
                    group: groupId,
                },
            });
            return res.data.videos;
        },
        enabled: !!groupId && !!sessionId, // avoids invalid calls
    });
}
