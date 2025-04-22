import React, { useState } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { themeBalham } from 'ag-grid-community';
// import { AllCommunityModule, ModuleRegistry } from "ag-grid-community";

// Register all Community features
// ModuleRegistry.registerModules([AllCommunityModule]);


interface Props {

}

const FreeFormExampleTable: React.FC<Props> = () => {
    const [rowData, setRowData] = useState([
        { make: "Tesla", model: "Model Y", price: 64950, electric: true },
        { make: "Ford", model: "F-Series", price: 33850, electric: false },
        { make: "Toyota", model: "Corolla", price: 29600, electric: false },
    ]);

    // Column Definitions: Defines the columns to be displayed.
    const [colDefs, setColDefs] = useState([
        { field: "make" },
        { field: "model" },
        { field: "price" },
        { field: "electric" }
    ]);  
  return (
    <div>
       <AgGridReact
            theme={themeBalham}
            rowData={rowData}
            columnDefs={colDefs}
        />
    </div>
  );
}
export default FreeFormExampleTable;