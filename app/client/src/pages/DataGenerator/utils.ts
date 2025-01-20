import { createContext, useContext } from 'react';
import { WizardCtxObj } from './types';

export const WizardCtx = createContext<WizardCtxObj | null>(null);
export const useWizardCtx = (): WizardCtxObj => {
    const context = useContext(WizardCtx);
    if (!context) {
      throw new Error('useWizardCtx must be used within a WizardProvider');
    }
    return context;
};