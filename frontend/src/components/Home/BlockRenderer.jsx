export default function BlockRenderer({ block }) {
    if (block.block_type === 'text') {
        return <div>{block.text_content}</div>;
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
