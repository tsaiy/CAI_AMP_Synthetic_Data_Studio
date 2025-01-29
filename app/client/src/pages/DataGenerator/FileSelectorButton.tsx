import get from 'lodash/get';
import { Button, Modal } from 'antd';
import React, { useState } from 'react';
import FilesTable from './FilesTable';
import { FileSearchOutlined } from '@ant-design/icons';
import { File, WorkflowType } from './types';


interface Props {
  onAddFiles: (files: File[]) => void;
  workflowType: WorkflowType;
}

const FileSelectorButton: React.FC<Props> = ({ onAddFiles, workflowType }) => {
  const [showModal, setShowModal] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])

  const onSelectedRows = (selections: File[]) => {
    console.log('onSelectedRows', selections);
    setSelectedFiles(selections);
  };

  const onFinish = () => {
    console.log('onFinish', selectedFiles);
    setShowModal(false);
    onAddFiles(selectedFiles);
    
  };

  return (
    <>
      <Button
        style={{ marginLeft: '4px' }}
        onClick={() => setShowModal(true)}
        icon={<FileSearchOutlined />}
      />
      {showModal && (
        <Modal
          visible={showModal}
          okText={`Add`}
          title={`File Selector`}
          onCancel={() => setShowModal(false)}
          onOk={() => onFinish()}
          width="60%"
        >
          <FilesTable onSelectedRows={onSelectedRows} workflowType={workflowType} />
        </Modal>
      )}
    </>
  );
};

export default FileSelectorButton;
