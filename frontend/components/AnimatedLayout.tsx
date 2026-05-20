"use client";

import { AnimatePresence, motion } from "framer-motion";
import { ReactNode } from "react";

interface Props {
  children: ReactNode;
}

export default function AnimatedLayout({ children }: Props) {
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={Date.now()}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        transition={{ duration: 0.3 }}
        className="flex-1"
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
