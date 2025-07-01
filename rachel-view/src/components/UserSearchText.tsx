// src/components/UserSearchText.tsx
import React, { useEffect, useRef, useState } from 'react';
import { BE_HOST, BE_PORT, BE_PROTOCOL } from '../sharedConfig';
import { useUIContext } from '../context/UIContext';
import { UserSearchContent } from './UserSearchContent';

interface UserSearchTextProps {
    segmentId: string;
    children: React.ReactNode;
}

export const UserSearchText = ({ segmentId, children }: UserSearchTextProps) => {
    const ref = useRef<HTMLDivElement>(null);
    const [selectionText, setSelectionText] = useState<string | null>(null);
    const { setModalOpen, setModalContent } = useUIContext();

    useEffect(() => {
        const handleMouseUp = () => {
            const selection = window.getSelection();
            if (!selection || selection.isCollapsed) return;

            const range = selection.getRangeAt(0);
            const selectionContent = selection.toString();
            if (!selectionContent || !ref.current?.contains(range.commonAncestorContainer)) return;

            setSelectionText(selectionContent);
        };

        const handleClick = (e: MouseEvent) => {

            const selection = window.getSelection();
            const selectionContent = selection?.toString();

            if (!selectionText || !selectionContent) return;

            const range = selection?.getRangeAt(0);
            if (range && range.toString() === selectionText) {
                const rect = range.getBoundingClientRect();
                const withinX = e.clientX >= rect.left && e.clientX <= rect.right;
                const withinY = e.clientY >= rect.top && e.clientY <= rect.bottom;

                if (withinX && withinY) {
                    setModalOpen(true);
                    setModalContent(<UserSearchContent
                        segmentId={segmentId}
                        selectedText={selectionText}
                    />);
                    return;
                }
            }

            setSelectionText(null);
        };

        document.addEventListener('mouseup', handleMouseUp);
        document.addEventListener('mousedown', handleClick);
        return () => {
            document.removeEventListener('mouseup', handleMouseUp);
            document.removeEventListener('mousedown', handleClick);
        };
    }, [selectionText]);

    return <div ref={ref}>{children}</div>;
};
