import { useStore } from '@/stores/user';

import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom';
import LibraryModal from './Library/LibraryModal';

export default function UserBar() {
    const user = useStore((state) => state.user)
    const logout = useStore.getState().logout;
    const logoutConfirm = () => {
        if (confirm("Are you sure you want to logout?")) {
            logout();
        }
    }
    const navigate = useNavigate();

    const [isModalOpen, setIsModalOpen] = useState(false);
    const closeModal = () => setIsModalOpen(false);
    const openModal = () => setIsModalOpen(true);


    return (
        <div className='my-auto'>
            {/* user img*/}
            <div className='flex items-center gap-2'>
                {user ? <img src={user?.picture} alt={user?.name} className='w-8 h-8 rounded-full' /> :
                    <div className='w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-white'>
                        U
                    </div>
                }
                <div className='flex-1'>
                    {user ? user.name : 'Guest'}
                </div>
                <div className='z-30 hover:bg-gray-800 p-2 rounded-full cursor-pointer transition' onClick={openModal}>
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
                        <path strokeLinecap="round" strokeLinejoin="round" d="m15.75 10.5 4.72-4.72a.75.75 0 0 1 1.28.53v11.38a.75.75 0 0 1-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 0 0 2.25-2.25v-9a2.25 2.25 0 0 0-2.25-2.25h-9A2.25 2.25 0 0 0 2.25 7.5v9a2.25 2.25 0 0 0 2.25 2.25Z" />
                    </svg>
                </div>
                <button className='bg-gray-800 px-2 py-1 rounded hover:bg-gray-700 cursor-pointer transition'
                    onClick={() => user ? logoutConfirm() : navigate('/login')}
                >
                    {user ? 'Logout' : 'Login'}
                </button>

                <LibraryModal isModalOpen={isModalOpen} closeModal={closeModal} />

            </div>
        </div>
    )
}
