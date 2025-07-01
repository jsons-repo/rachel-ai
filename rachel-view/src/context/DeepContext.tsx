import React, { createContext, useContext, useState, ReactNode } from 'react';
import { DeepSearchResponse } from '../types';

// DeepContext tracks multiple results per segment ID

type DeepContextType = {
    deepSearchResults: Map<string, DeepSearchResponse[]>;
    setDeepSearchResults: React.Dispatch<React.SetStateAction<Map<string, DeepSearchResponse[]>>>;

    userSearchResults: Map<string, string[]>;
    setUserSearchResults: React.Dispatch<React.SetStateAction<Map<string, string[]>>>;
};

const DeepContext = createContext<DeepContextType | undefined>(undefined);

export const useDeepContext = (): DeepContextType => {
    const context = useContext(DeepContext);
    if (!context) throw new Error('useDeepContext must be used within DeepProvider');
    return context;
};

export const DeepProvider = ({ children }: { children: ReactNode }) => {
    const [deepSearchResults, setDeepSearchResults] = useState<Map<string, DeepSearchResponse[]>>(new Map());
    const [userSearchResults, setUserSearchResults] = useState<Map<string, string[]>>(new Map());

    return (
        <DeepContext.Provider value={{
            deepSearchResults,
            setDeepSearchResults,
            userSearchResults,
            setUserSearchResults,
        }}>
            {children}
        </DeepContext.Provider>
    );
};
