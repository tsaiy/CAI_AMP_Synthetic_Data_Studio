import { createContext, useContext } from 'react';
import { WizardCtxObj } from './types';
import moment from 'moment';
import toString from 'lodash/toString';

export const WizardCtx = createContext<WizardCtxObj | null>(null);
export const useWizardCtx = (): WizardCtxObj => {
    const context = useContext(WizardCtx);
    if (!context) {
      throw new Error('useWizardCtx must be used within a WizardProvider');
    }
    return context;
};


const DIRECTORY_MIME_TYPE = 'inode/directory';

export const getFileSize = (bytes: number, si: boolean) => {
  const unit = si ? 1000 : 1024;
  if (bytes < unit) {
    return bytes + ' B';
  }
  const exp = Math.floor(Math.log(bytes) / Math.log(unit));
  let prefix = 'kMGTPE'.charAt(exp - 1);
  if (!si) {
    prefix += 'i';
  }
  return parseFloat(toString(bytes / Math.pow(unit, exp))).toFixed(2) + ' ' + prefix + 'B';
};

export const isDirectory = (file: File) => file?.mime === DIRECTORY_MIME_TYPE;

export const fromNow = time => {
  if (time === null || time === undefined) {
    return 'Never';
  }
  return moment(time).fromNow();
};
