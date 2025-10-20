import React from 'react'
import HistoryConversations from './components/HistoryConversations'
import VideosInConversation from './components/VideosInConversation/VideosInConversation'
import UserBar from './components/UserBar'

export default function Sidebar() {

    return (
        <div className='h-screen min-w-[300px] max-w-[300px] max-md:hidden block bg-black/90 text-gray-400'>
            <div className='h-[45%] overflow-y-auto'>
                <HistoryConversations />
            </div>
            <div className='h-[45%] overflow-y-auto'>
                <VideosInConversation />
            </div>
            <div className='h-[10%] border-t border-gray-800 p-2'>
                <UserBar />
            </div>
        </div>
    )
}
