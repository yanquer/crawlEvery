// @ts-ignore
import {Box, Flex, ScrollArea, Theme, ThemePanel, Text, Heading, Button} from "@radix-ui/themes";
import {type ReactNode, useEffect, useState} from "react";
import {WsClient} from "../common/ws_/simple-ws-client";


export const LeftArea = ({areaTitle="运行日志"}) => {

    const [text, setText] = useState<Array<ReactNode>>([]);

    useEffect(() => {

        WsClient.shared?.subscribe('log', async (data) => {
            // console.log(data);
            if (data){
                setText((lastData) => {
                    lastData.push(
                        <Text as="p">
                            [{data.timestamp}]{data.data}
                        </Text>
                    )
                    console.log('lastData')
                    console.log(lastData)
                    return [...lastData];
                });
            }
        }).then()

    }, [])

    return <Box width={'50%'} height={'100%'} p={'4'}
        // className={'bg-gray-800'}
    >
        <Flex width={'100%'} height={'100%'}
              justify={'center'}
              direction={'column'}
              // className={'bg-gray-800'}
        >
            <Heading size="4" m="2" trim="start"
                     align={'center'}
                     color="gold">
                {areaTitle}
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

    return <LeftArea areaTitle={'阶段汇总'} />;
}

export const ListenRooms = ({areaTitle="已在监听的直播间"}) => {

    const [text, setText] = useState<Array<ReactNode>>([]);

    useEffect(() => {

        WsClient.shared?.subscribe('room', async (data) => {
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

    return <Box width={'100%'} height={'100%'} p={'4'}
        // className={'bg-gray-800'}
    >
        <Flex width={'100%'} height={'100%'}
              justify={'center'}
              direction={'column'}
            // className={'bg-gray-800'}
        >
            <Heading size="4" m="2" trim="start"
                     align={'center'}
                     color="gold">
                {areaTitle}
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


export const ButtonGroupUtil = () => {
    return <Box width={'100%'} height={'100%'} p={'4'}
        // className={'bg-gray-800'}
    >

        <Button >请求重启</Button>
    </Box>
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

    const invert = 20
    return <Theme className={'w-full h-full'}
                  appearance="dark"
                  accentColor="iris" grayColor="sand" scaling="95%"
    >
        <Box className={'w-full h-full'}
            style={{
                background: 'url(/images/bg1.jpeg)',
                backgroundRepeat: "no-repeat",
                backgroundSize: "cover",
                backgroundPosition: "center",
                filter: `blur(50px) grayscale(55%) ${invert ? "invert(" + invert + "%)" : ""}`,
                // backdropFilter: `blur(50px) grayscale(55%) ${invert ? "invert(" + invert + "%)" : ""}`,
                zIndex: "-1",
                opacity: "0.99",
            }}
        >
        </Box>

        <Box className={"w-full h-full absolute top-0 left-0 rounded-xl"}>

            <Flex
                gap={"2"}
                pb={"4px"}
                direction={'column'}
                height={"100%"}
                width={"100%"}
                justify={"center"}
            >

                <Flex
                    gap={"2"}
                    pb={"4px"}
                    direction={'row'}
                    height={"20%"}
                    width={"100%"}
                    justify={"center"}
                >
                   <Box width={'100%'} height={'100%'}>
                       <Flex
                            justify={'center'}
                            width={'100%'}
                            height={'100%'}
                            direction={'row'}
                       >

                       {/*  监听窗口  */}
                           <ListenRooms />
                           {/*<ButtonGroupUtil/>*/}

                       </Flex>
                   </Box>
                </Flex>

                <Flex
                    gap={"2"}
                    pb={"4px"}
                    direction={'row'}
                    height={"80%"}
                    width={"100%"}
                    justify={"center"}
                >
                    <LeftArea />
                    <RightArea />
                </Flex>
            </Flex>

        </Box>


        {/*<ThemePanel />*/}
    </Theme>
}


