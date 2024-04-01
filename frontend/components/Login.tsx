"use client";

import React from "react";
import { signIn } from "next-auth/react";

type Props = {};

function Login({}: Props) {
  return (
    <div className="bg-[#11A37F] h-screen flex flex-col items-center justify-center text-center">
      <img
        src="https://upload.wikimedia.org/wikipedia/commons/1/13/ChatGPT-Logo.png"
        alt="logo"
        className="w-96"
      />
      <button
        onClick={() => signIn("google")}
        className="text-white font-bold text-3xl animate-pulse"
      >
        Sign In to use ChatGpt
      </button>
    </div>
  );
}

export default Login;
