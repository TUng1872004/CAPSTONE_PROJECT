import { create } from "zustand";
import { persist } from "zustand/middleware";

export const useStore = create(
    persist(

        (set, get) => ({
            session_id: null, // new chat
            setSessionId: (session_id) => set({ session_id }),
            getSessionId: () => get().session_id,

            chatMessages: [],
            setChatMessages: (messages) => set({ chatMessages: messages }),
            addChatMessage: (message) => set({ chatMessages: [...get().chatMessages, message] }),
            clearChatMessages: () => set({ chatMessages: [] }),


            chatHistory: [],
            setChatHistory: (history) => set({ chatHistory: history }),
            addChatHistory: (chat) => set({ chatHistory: [...get().chatHistory, chat] }),
            clearChatHistory: () => set({ chatHistory: [] }),


            workspaceVideos: [],
            setWorkspaceVideos: (videos) => set({ workspaceVideos: videos }),
            clearWorkspaceVideos: () => set({ workspaceVideos: [] }),
            removeWorkspaceVideo: (videoId) => set({ workspaceVideos: get().workspaceVideos.filter(v => v.id !== videoId) }),
            addWorkspaceVideo: (video) => set({ workspaceVideos: [...get().workspaceVideos, video] }),


            currentGroup: null,
            setCurrentGroup: (group) => set({ currentGroup: group }),
        }),
        {
            name: "chatState", // key in localStorage
            partialize: (state) => ({
                session_id: state.session_id,
                currentGroup: state.currentGroup,
            })
        }
    )
);
