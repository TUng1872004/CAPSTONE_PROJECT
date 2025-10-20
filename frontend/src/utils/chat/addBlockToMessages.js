import mergeBlock from "./mergeBlock";

export default function addBlockToMessages(messages, role, newBlock) {
    const lastMessage = messages[messages.length - 1];

    if (lastMessage && lastMessage.role === role) {
        const newMessages = [...messages];
        const messagesCopy = {...lastMessage};
        const blocksCopy = [...messagesCopy.blocks];

        const lastBlock = blocksCopy[blocksCopy.length - 1];

        if (!mergeBlock(lastBlock, newBlock)){
            blocksCopy.push(newBlock);
        }

        messagesCopy.blocks = blocksCopy;
        newMessages[newMessages.length - 1] = messagesCopy;
        return newMessages;
    }
    return [...messages, { role, blocks: [newBlock] }];
}