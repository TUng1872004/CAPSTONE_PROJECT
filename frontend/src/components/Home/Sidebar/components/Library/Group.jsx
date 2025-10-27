import React from 'react'
import { useStore } from "@/stores/chat";
import clsx from 'clsx';
import GroupDropdownList from './GroupDropdownList';

export default function Group({ group }) {
  const currentGroup = useStore((state) => state.currentGroup);

  const setCurrentGroup = useStore((state) => state.setCurrentGroup);
  
  const handleSelectGroup = () => {
    setCurrentGroup(group._id);
  }

  return (  
    <div className={clsx('relative p-2 m-1 hover:bg-gray-100 rounded-md cursor-pointer', {
      'bg-gray-200 text-gray-800': currentGroup === group._id
    })} 
    onClick={handleSelectGroup}
    >
      <div className='truncate mr-2'>{group.name}</div>
      <div className="absolute top-2 right-0 rounded-full p-1 hover:bg-gray-200 cursor-pointer">
        <GroupDropdownList group={group} />
      </div>
    </div>
  )
}
