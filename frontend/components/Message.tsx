"use client";

import { DocumentData } from "firebase/firestore";
import { motion } from "framer-motion";

import React from "react";

type Props = {
  message: DocumentData;
};

function Message({ message }: Props) {
  const isChatGPT = message.user.name === "ChatGPT";
  const messageData = splitString(message.text);
  console.log(messageData[1]?.split('/n')[0].replace("jsx", '').replace('/n', ''));
  return (
    <motion.div
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      className={`py-5 text-white ${isChatGPT && "bg-[#434654]"}`}
    >
      <div className="flex flex-col gap-4 space-x-5 px-10 max-w-2xl mx-auto">
        <img src={message.user.avatar} alt="" className="h-8 w-8" />
        <h1 className="text-xl font-medium text-neutral-50">{messageData[0]}</h1>
        {messageData[1] ? (
          <div
            dangerouslySetInnerHTML={{
              __html: messageData[1]?.split('/n')[0].replace("jsx", '').replace('/n', '').replace('html', '')
            }}
          />
        ) : (
          <></>
        )}

        <p className="text-lg text-neutral-50">{messageData[2]}</p>


      </div>
    </motion.div>
  );
}

const splitString = (response: string) => {
  const res = response.split("```");
  // Check for table, list, or paragraph
  if (res.length === 3) {
    const tableRegex = /(\|.*\|)+/g; // Table regex
    const listRegex = /(\*\s.*\n)+/g; // List regex
    const paragraphRegex = /(\n\s*\n)+/g; // Paragraph regex
    // Check if it's a table
    if (tableRegex.test(res[1])) {
      return ['Table', res[1], res[2]];
    }
    // Check if it's a list
    else if (listRegex.test(res[1])) {
      return ['List', res[1], res[2]];
    }
    // Check if it's a paragraph
    else if (paragraphRegex.test(res[1])) {
      return ['Paragraph', res[1], res[2]];
    }
  }
  return res;
};

export default Message;
