import { Navigate, createBrowserRouter } from "react-router-dom";
import Layout from "./Container";
import DataGenerator from "./pages/DataGenerator";
import Evaluator from "./pages/Evaluator";
import HomePage from "./pages/Home";
import HistoryPage from "./pages/History";
import RouteAccessControl from './components/RouteAccessControl'
import { Pages } from "./types";
import EvaluatorPage from "./pages/Evaluator";
import ReevaluatorPage from "./pages/Evaluator/ReevaluatorPage";


const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout/>,
    children: [
      {
        path: '/', // Redirect root to Pages.GENERATOR
        element: <Navigate to={Pages.HOME} replace />,
      },
      { path: Pages.HOME, element: <HomePage key={Pages.HOME}/>, loader: async () => null},
      { path: Pages.GENERATOR, element: <DataGenerator key={Pages.GENERATOR}/>, loader: async () => null},
      // {
      //   path: Pages.EVALUATOR,
      //   element:(
      //      <RouteAccessControl
      //       element={<Evaluator key={Pages.EVALUATOR}/>}
      //       validator={state => state.internalRedirect === true}
      //     />
      //   ),
      //   loader: async () => null
      // },
      { path: Pages.HISTORY, element: <HistoryPage key={Pages.HISTORY}/>, loader: async () => (null) },
      {
        path: `${Pages.EVALUATOR}/create/:generate_file_name`,
        element: <EvaluatorPage />,
        // element:(
        //    <RouteAccessControl
        //     element={<Evaluator/>}
        //     validator={state => state.internalRedirect === true}
        //   />
        // ),
        loader: async () => null
      },
      {
        path: `${Pages.EVALUATOR}/reevaluate/:evaluate_file_name`,
        element: <ReevaluatorPage />,
        loader: async () => null
      },
      { path: Pages.HISTORY, element: <HistoryPage/>, loader: async () => (null) },
      // { path: Pages.DATASETS, element: <Datasets/>, loader: async () => (null) },
    ]
  },
]);


export default router;