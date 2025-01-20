import { Tabs } from "antd";
import Evaluations from "../../components/Evaluations";
import DatasetsComponent from "../../components/Datasets";

const historyPageStyle = {
    height: "100%",
}

const historyPageTabsStyle = {
    height: "100%",
    backgroundColor: "white",
    padding: "15px"
}

export default function HistoryPage() {
    return (
        <div style={historyPageStyle}>
            <h1>History</h1>
            <Tabs
                tabPosition="left"
                items={[
                    {
                        label: `Datasets`,
                        key: `datasets`,
                        children: <DatasetsComponent></DatasetsComponent>,
                    },
                    {
                        label: `Evaluations`,
                        key: `evaluations`,
                        children: <Evaluations></Evaluations>,
                    }
                ]}
                style={historyPageTabsStyle}
            />
        </div>
    );
};