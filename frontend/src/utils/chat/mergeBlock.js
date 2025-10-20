export default function mergeBlock(lastBlock, newBlock) {
    if (!lastBlock || !newBlock) return false;
    
    if (lastBlock.block_type === 'text' && newBlock.block_type === 'text') {
        lastBlock.text_content += newBlock.text_content;
        return true;
    }
    if (lastBlock.block_type === 'image' && newBlock.block_type === 'image') {
        lastBlock.image_urls = lastBlock.image_urls.concat(newBlock.image_urls);
        return true;
    }
    if (lastBlock.block_type === 'video' && newBlock.block_type === 'video') {
        lastBlock.video_urls = lastBlock.video_urls.concat(newBlock.video_urls);
        return true;
    }
    return false;    
}