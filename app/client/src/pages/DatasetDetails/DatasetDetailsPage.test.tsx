import { beforeEach, describe, test } from 'vitest';
import { render } from '@testing-library/react';
import DatasetDetailsPage from './DatasetDetailsPage';
import { QueryClient, QueryClientProvider } from 'react-query';

describe('DatasetDetailsPage', () => {
    let queryClient: QueryClient;

    beforeEach(() => {
        queryClient = new QueryClient();
    });
    test('Renders the page', () => {
        render(<QueryClientProvider client={queryClient}><DatasetDetailsPage /></QueryClientProvider>);
    });
});