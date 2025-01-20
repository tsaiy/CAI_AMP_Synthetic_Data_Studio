import { Modal, Button } from "antd";
import { DatasetResponse } from "../../../api/Datasets/response";
import DatasetDetail from "./DatasetDetail";
import { Dataset } from "../../../pages/Evaluator/types";

export type DatasetDetailModalProps = {
  datasetDetails: DatasetResponse | Dataset;
  isModalActive: boolean;
  setIsModalActive: (isActive: boolean) => void;
}

export default function DatasetDetailModal({ isModalActive, setIsModalActive, datasetDetails }: DatasetDetailModalProps) {
  return (
    <Modal title={`View Dataset Details`} width={"80%"} open={isModalActive} onCancel={() => setIsModalActive(false)} onOk={() => setIsModalActive(false)} footer={<Button type="primary" onClick={() => setIsModalActive(false)}>Ok</Button>}>
      <DatasetDetail datasetDetails={datasetDetails} />
    </Modal>
  )
}