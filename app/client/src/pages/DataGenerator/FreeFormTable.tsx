
import isEmpty from 'lodash/isEmpty';
import first from 'lodash/first';
import toString from 'lodash/toString';
import React, { FunctionComponent, useState, useMemo, useCallback, useEffect } from 'react';
import { AgGridReact } from 'ag-grid-react';
// // Register all Community features
// // ModuleRegistry.registerModules([AllCommunityModule]);
import { themeMaterial } from 'ag-grid-community';

import { 
    ModuleRegistry, 
    ClientSideRowModelModule, 
    ValidationModule,
    type ColDef,
    type GetRowIdFunc,
    type GetRowIdParams
 } from 'ag-grid-community';

// import { RowGroupingModule } from 'ag-grid-community'; 
// import { PivotModule } from 'ag-grid-community'; 
// import { TreeDataModule } from 'ag-grid-community';
// import { ClientSideRowModelModule } from 'ag-grid-community';
// import { AllModules } from 'ag-grid-community';
import { TextFilterModule } from 'ag-grid-community'; 
import { NumberFilterModule } from 'ag-grid-community'; 
import { DateFilterModule } from 'ag-grid-community'; 
// import { SetFilterModule } from 'ag-grid-community'; 
// import { MultiFilterModule } from 'ag-grid-community'; 
// import { GroupFilterModule } from 'ag-grid-community'; 
// import { CustomFilterModule } from 'ag-grid-community'; 

// Register all Community features (if needed, specify valid modules here)
ModuleRegistry.registerModules([
    // AllModules,
    TextFilterModule,
    NumberFilterModule,
    DateFilterModule,
    ClientSideRowModelModule,
    ValidationModule
]);

interface Props {
    data: Record<string, unknown>[];
}

const FreeFormTable: FunctionComponent<Props> = ({ data }) => {
    const [colDefs, setColDefs] = useState([]);
    const [rowData, setRowData] = useState([]);
    
    useEffect(() => {
        if (!isEmpty(data)) {
            const columnNames = Object.keys(first(data));
            const columnDefs = columnNames.map((colName) => ({
                field: colName,
                headerName: colName,
                width: 250,
                filter: true,
                sortable: true,
                resizable: true
            }));
            setColDefs(columnDefs);
            setRowData(data);
        }
    }
    , [data]);
    // const [rowData, setRowData] = useState([
    //     { make: "Tesla", model: "Model Y", price: 64950, electric: true },
    //     { make: "Ford", model: "F-Series", price: 33850, electric: false },
    //     { make: "Toyota", model: "Corolla", price: 29600, electric: false },
    // ]);

    // // Column Definitions: Defines the columns to be displayed.
    // const [colDefs, setColDefs] = useState([
    //     { field: "make" },
    //     { field: "model" },
    //     { field: "price" },
    //     { field: "electric" }
    // ]); 
    
    const defaultColDef: ColDef = useMemo(
        () => ({
          flex: 1,
          filter: true,
          enableRowGroup: true,
          enableValue: true,

          editable: true,
          minWidth: 170
        }),
        []
      );
    
      let index = 0;
      const getRowId = useCallback<GetRowIdFunc>(
        ({ data: { ticker } }: GetRowIdParams) => {
            index++;
            return ticker || toString(index);
        },
        []
      );
    
      const statusBar = useMemo(
        () => ({
          statusPanels: [
            { statusPanel: "agTotalAndFilteredRowCountComponent" },
            { statusPanel: "agTotalRowCountComponent" },
            { statusPanel: "agFilteredRowCountComponent" },
            { statusPanel: "agSelectedRowCountComponent" },
            { statusPanel: "agAggregationComponent" },
          ],
        }),
        []
      );

  
  return (
    <>
      <div style={{ 
        // minHeight: '600px', 
        xScroll: 'auto', 
        yScroll: 'auto',
        height: '600px',
        display: 'flex',
        flexDirection: 'column'
        }}>
        <AgGridReact
          theme={themeMaterial}
          columnDefs={colDefs}
          rowData={rowData}
          getRowId={getRowId}
          defaultColDef={defaultColDef}
          statusBar={statusBar}
        />
      </div>
    </>
  );
}
export default FreeFormTable;