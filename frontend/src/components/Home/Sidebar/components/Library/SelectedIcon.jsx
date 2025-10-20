import { CheckIcon, XMarkIcon } from "@heroicons/react/16/solid"
export default function SelectedIcon({ selected }) {
    return (
        selected ? <CheckIcon className="h-5 w-5 text-green-500" /> : <XMarkIcon className="h-5 w-5 text-red-500" />
    )
}
