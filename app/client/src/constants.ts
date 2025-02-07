import { ModelParameters, Pages } from "./types";

export const LABELS = {
    [Pages.HOME]: 'Home',
    [Pages.GENERATOR]: 'Generation',
    [Pages.EVALUATOR]: 'Evaluator',
    [Pages.DATASETS]: 'Datasets',
    [Pages.HISTORY]: 'History',
    [Pages.FEEDBACK]: 'Feedback',
    [ModelParameters.TEMPERATURE]: 'Temperature',
    [ModelParameters.TOP_K]: 'Top K',
    [ModelParameters.TOP_P]: 'Top P',
    [ModelParameters.MAX_TOKENS]: 'Max Tokens'
};

export const TRANSLATIONS: Record<string, string> = {
    "code_generation": "Code Generation",
    "text2sql": "Text to SQL"
  };

export const CDSW_PROJECT_URL = import.meta.env.VITE_CDSW_PROJECT_URL;
export const IS_COMPOSABLE = import.meta.env.VITE_IS_COMPOSABLE;
