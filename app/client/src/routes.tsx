import { Navigate, createBrowserRouter } from "react-router-dom";
import Layout from "./Container";
import DataGenerator from "./pages/DataGenerator";
import HomePage from "./pages/Home";
import { Pages } from "./types";
import EvaluatorPage from "./pages/Evaluator";
import ReevaluatorPage from "./pages/Evaluator/ReevaluatorPage";
import DatasetDetailsPage from "./pages/DatasetDetails/DatasetDetailsPage";
import WelcomePage from "./pages/Home/WelcomePage";


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
      {
        path: `${Pages.EVALUATOR}/create/:generate_file_name`,
        element: <EvaluatorPage />,
        loader: async () => null
      },
      {
        path: `${Pages.EVALUATOR}/reevaluate/:evaluate_file_name`,
        element: <ReevaluatorPage />,
        loader: async () => null
      },
      {
        path: `dataset/:generate_file_name`,
        element: <DatasetDetailsPage />,
        loader: async () => null
      },
      {
        path: `welcome`,
        element: <WelcomePage />,
        loader: async () => null
      }
    ]
  },
]);


export default router;