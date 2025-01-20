import { FC } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';


interface Props {
    text: string;
}

/**
 * Renders markdown w/ language specific syntax-highlighting
 */
const Markdown:FC<Props> = ({ text }) => {
    return (
        <ReactMarkdown
            children={text}
            components={{
                code(props) {
                    const {children, className, ...rest} = props;
                    const match = /language-(\w+)/.exec(className || '');
                    return match ? (
                        <SyntaxHighlighter
                            language={match[1]}
                            style={oneLight}
                            children={String(children).replace(/\n$/, '')}
                            PreTag='div'
                            {...rest}
                        />
                    ) : (
                    <code className={className} {...rest} >
                        {children}
                    </code>
                    )
                }
            }}
        />
    )
}

export default Markdown;