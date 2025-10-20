import clsx from "clsx";

export default function BlockRenderer({ block, role }) {
    if (block.block_type === 'text') {
        //  check if user or assistant
        // .role === 'user' or 'assistant'
        return <div
            className={clsx(
                'max-w-[75%] px-4 py-2 my-2 rounded-lg text-sm whitespace-pre-wrap break-all',
                role === 'user'
                    ? 'bg-gray-700 text-white self-end' // user: right
                    : 'bg-gray-200 text-black self-start' // bot: left
            )}
        >
            {block?.text_content}
        </div>
    }

    if (block.block_type === 'image') {
        return (
            <div className="grid grid-cols-3 gap-2">
                {block.image_urls.map((url, i) => (
                    <img key={i} src={url} className="w-full rounded-lg" />
                ))}
            </div>
        );
    }

    if (block.block_type === 'video') {
        return (
            <div className="grid grid-cols-3 gap-2">
                {block.video_urls.map((url, i) => (
                    <video key={i} src={url} controls className="w-full rounded-lg" />
                ))}
            </div>
        );
    }

    return null;
}
