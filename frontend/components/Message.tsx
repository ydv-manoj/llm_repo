"use client";

import { DocumentData } from "firebase/firestore";
import { motion } from "framer-motion";
import React from "react";
import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import './Components.css'

type Props = {
  message: DocumentData;
};

function Message({ message }: Props) {
  const isChatGPT = message.user.name === "ChatGPT";

  return (
    <motion.div
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      className={`py-5 text-white ${isChatGPT && "bg-[#434654]"}`}
    >
      <div className="flex space-x-5 px-10 max-w-5xl mx-auto">
        <img src={message.user.avatar} alt="" className="h-8 w-8" />
        {/* <p className="pt-1 text-sm">{message.text}</p> */}
        <Markdown className="text-sm border-10px markdown_comp" remarkPlugins={[remarkGfm]}>{message.text}</Markdown>
      </div>
    </motion.div>
  );
}

export default Message;
