import { Typography } from "antd";
import moment from "moment";

const { Text } = Typography;

export type DateTimeProps = {
    dateTime: string;
    inputFormat?: string;
    outputFormat?: string;
}

/**
 * DateTime component
 * @param dateTime - The date and time string to be formatted
 * @param inputFormat - The format of the input date and time string (default: 'YYYY MM DD HH mm ss')
 * @param outputFormat - The format of the output date and time string (default: 'YYYY/MM/DD HH:mm:ss')
 */
export default function DateTime({dateTime, inputFormat = 'YYYY MM DD HH mm ss', outputFormat = 'YYYY/MM/DD HH:mm:ss'}: DateTimeProps) {

    return (
        <Text>{moment(dateTime, inputFormat).format(outputFormat).toString()}</Text>
    )
}