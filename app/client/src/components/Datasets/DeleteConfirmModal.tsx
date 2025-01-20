import { Button, Flex, Modal, Typography } from "antd"
import { DatasetResponse } from "../../api/Datasets/response";
import { styled } from "styled-components";

const { Text } = Typography;

const ModalButtonGroup = styled(Flex)`
    margin-top: 15px !important;
`

type DeleteConfirmWarningModalProps = { 
    row: DatasetResponse
    handleDeleteEvaluationConfirm: () => void
}


export default function DeleteConfirmWarningModal({ row, handleDeleteEvaluationConfirm }: DeleteConfirmWarningModalProps) {

    return Modal.warning({
        title: 'Remove Dataset',
        closable: true,
        content: (
            <>
                <Text>
                    {`Are you sure you want to remove this dataset`} <Text strong>{row.display_name}?</Text>
                </Text>
            </>
        ),
        icon: undefined,
        footer: (
            <ModalButtonGroup gap={8} justify='end'>
                <Button onClick={() => Modal.destroyAll()}>{'Cancel'}</Button>
                <Button
                    onClick={() => {
                        handleDeleteEvaluationConfirm()
                        Modal.destroyAll()
                    }}
                    type='primary'
                    color='danger'
                    variant='solid'
                >
                    {'Remove'}
                </Button>
            </ModalButtonGroup>
        ),
        maskClosable: true,
        width: "20%"
    })
}