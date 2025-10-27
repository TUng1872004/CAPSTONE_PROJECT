// components/Modal.tsx

import { Description, Dialog, DialogPanel, DialogTitle } from "@headlessui/react";
import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/react'
import {
    ArchiveBoxXMarkIcon,
    ChevronDownIcon,
    EllipsisVerticalIcon,
    PencilIcon,
    Square2StackIcon,
    TrashIcon,
} from '@heroicons/react/16/solid'


export default function Modal({
    isOpen,
    onClose,
    title,
    children,
}) {
    return (
        <Dialog 
        open={isOpen} 
        transition
        className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4 transition duration-300 ease-out data-closed:opacity-0"
        onClose={onClose}>
            <DialogPanel
                className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-6 relative w-[70vw] max-w-5xl"
            >
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:hover:text-white"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
                    </svg>
                </button>
                {title && (
                    <DialogTitle className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                        {title}
                    </DialogTitle>
                )}
                <div>
                    {children}
                </div>
            </DialogPanel>
        </Dialog>
    );
}
