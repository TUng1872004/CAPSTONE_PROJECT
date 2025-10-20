export default function mergeBlock(lastBlock, newBlock) {
    if (!lastBlock || !newBlock) return false;

    if (lastBlock.blockType === 'text' && newBlock.blockType === 'text') {
        lastBlock.textContent += newBlock.textContent;
        return true;
    }
    if (lastBlock.blockType === 'image' && newBlock.blockType === 'image') {
        lastBlock.image_urls = lastBlock.image_urls.concat(newBlock.image_urls);
        return true;
    }
    if (lastBlock.blockType === 'video' && newBlock.blockType === 'video') {
        lastBlock.video_urls = lastBlock.video_urls.concat(newBlock.video_urls);
        return true;
    }
    return false;    
}