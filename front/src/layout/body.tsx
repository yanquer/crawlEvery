import {Box, Flex, ScrollArea, Theme, ThemePanel, Text, Heading} from "@radix-ui/themes";
import {type ReactNode, useEffect, useState} from "react";
import {WsClient} from "../common/ws_/simple-ws-client";


export const LeftArea = () => {

    const [text, setText] = useState<Array<ReactNode>>([]);

    useEffect(() => {

        WsClient.shared?.subscribe('log', async (data) => {
            // console.log(data);
            if (data){
                setText((lastData) => {
                    lastData.push(
                        <Text as="p">
                            {data.data}
                        </Text>
                    )
                    console.log('lastData')
                    console.log(lastData)
                    return [...lastData];
                });
            }
        }).then()

    }, [])

    return <Box width={'50%'} height={'100%'} p={'4'}>
        <Flex width={'100%'} height={'100%'}
              justify={'center'}
              direction={'column'}
        >
            <Heading size="4" m="2" trim="start"
                     align={'center'}
                     color="gold">
                运行日志
            </Heading>

            <ScrollArea type="always" scrollbars="vertical" style={{ height: '80%' }}>
                <Box p="2" pr="8">
                    {/*<Heading size="4" mb="2" trim="start">*/}
                    {/*    Principles of the typographic craft*/}
                    {/*</Heading>*/}
                    <Flex direction="column" gap="4">
                        {...text}
                    </Flex>
                </Box>
            </ScrollArea>
        </Flex>
    </Box>
}
export const RightArea = () => {

    return <LeftArea />;
}



export const Body = () => {

    useEffect(() => {

        for (let i = 0; i < 3; i++) {
            try {
                // WsClient.shared = new WsClient('http://localhost:8091/ws/room');
                WsClient.shared = new WsClient('ws://localhost:8091/ws/room');
                break;
            } catch (e) {
                console.error(e);
            }
        }

    }, [])

    return <Theme className={'w-full h-full'}
                  appearance="dark"
                  accentColor="iris" grayColor="sand" scaling="95%"
    >
        <Box className={'w-full h-full'}>

            <Flex
                gap={"2"}
                pb={"4px"}
                direction={'row'}
                height={"100%"}
                width={"100%"}
                justify={"center"}
            >
                <LeftArea />
                <RightArea />
            </Flex>

        </Box>

        <ThemePanel />
    </Theme>
}


