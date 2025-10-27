import React, { useState } from 'react'
import { messagesConversations } from '@/mockdata/messages'
import { useQuery } from 'react-query';
import api from '@/api/api';
import { useStore } from '@/stores/user';
import { useStore as useStoreChat } from "@/stores/chat";

import clsx from 'clsx';

export default function HistoryConversations() {
  const chatHistory = useStoreChat((state) => state.chatHistory);
  const setChatHistory = useStoreChat((state) => state.setChatHistory);
  const setSessionId = useStoreChat((state) => state.setSessionId);
  const session_id = useStoreChat((state) => state.session_id);
  const setChatMessages = useStoreChat((state) => state.setChatMessages);
  const setWorkspaceVideos = useStoreChat((state) => state.setWorkspaceVideos);
  const user = useStore((state) => state.user);

  useQuery(
    {
      queryKey: ["chatHistory", user],
      queryFn: async () => {
        const response = await api.get('/api/user/chat-history');
        const chats = response.data.chats;
        return chats;
      },
      onSuccess: (data) => {
        setChatHistory(data);
        if (data.length > 0) {
          if (!session_id) {
            setSessionId(data[0].session_id);
          }
        }
      },
      enabled: !!user,
    }
  );

  function createNewChat() {
    // set session id to null
    setSessionId(null);
    setChatMessages([]);
    setWorkspaceVideos([]);
  }

  function selectConversation(session_id) {
    // set session id 
    setSessionId(session_id);
  }

  return (
    <div className='relative flex flex-col h-full '>
      <div className='border-b border-gray-800 flex items-center justify-between sticky top-0 bg-black/90 p-2 '>
        <p className='text-sm p-2 text-gray-400/60'>Chats</p>
        {/* delete logic */}
        <div className='btn-icon' onClick={createNewChat}>
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
          </svg>
        </div>
      </div>
      <div className='flex flex-col scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-300 overflow-y-auto'>
        {
          chatHistory.map((conv, idx) => (
            <div key={idx}
              className={clsx('m-1 py-2 px-4 hover:bg-gray-800 cursor-pointer rounded-lg',
                (session_id === conv._id) ? 'bg-gray-800' : ''
              )}
              onClick={() => selectConversation(conv._id)}>
              <div className='text-sm '>{conv?._id?.slice(0, 8)}</div>
            </div>
          ))
        }
      </div>
    </div>
  )
}
