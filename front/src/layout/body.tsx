// @ts-ignore
import {Box, Flex, ScrollArea, Theme, ThemePanel, Text, Heading, Button, Badge, Grid} from "@radix-ui/themes";
import {type ReactNode, useEffect, useState} from "react";
import {WsClient} from "../common/ws_/simple-ws-client";


export const LeftArea = ({
                             areaTitle="运行日志",
                             subEvent="log",
                         }) => {

    const [text, setText] = useState<Array<ReactNode>>([]);

    useEffect(() => {

        WsClient.shared?.subscribe(subEvent, async (data) => {
            // console.log(data);
            if (data){
                setText((lastData) => {
                    lastData.push(
                        <Text as="p" key={lastData.length+1}>
                            {/*[{data.timestamp}]*/}
                            {data.data}
                        </Text>
                    )
                    // console.log('lastData')
                    // console.log(lastData)
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

    return <LeftArea areaTitle={'礼物消息'} subEvent={'gift'} />;
}

export const ListenRooms = ({areaTitle="已在监听的直播间"}) => {

    const [text, setText] = useState<Array<ReactNode>>([]);

    useEffect(() => {
        // const rooms: Array<string> = [
        //     "123123", "2342354", "2342342", "345345345", "3454353", "345345345",
        //     "123123", "2342354", "2342342", "345345345", "3454353", "345345345",
        //     "123123", "2342354", "2342342", "345345345", "3454353", "345345345",
        //     "123123", "2342354", "2342342", "345345345", "3454353", "345345345",
        //     "123123", "2342354", "2342342", "345345345", "3454353", "345345345",
        //     "123123", "2342354", "2342342", "345345345", "3454353", "345345345",
        //     "123123", "2342354", "2342342", "345345345", "3454353", "345345345",
        //     "123123", "2342354", "2342342", "345345345", "3454353", "345345345",
        //     "123123", "2342354", "2342342", "345345345", "3454353", "345345345",
        //     "123123", "2342354", "2342342", "345345345", "3454353", "345345345",
        //     "123123", "2342354", "2342342", "345345345", "3454353", "345345345",
        //     "123123", "2342354", "2342342", "345345345", "3454353", "345345345",
        // ];
        //
        // setText(
        //     rooms.map((r, idx) =>
        //             <div className={'m-1 inline'}>
        //                 <Badge
        //                     size={'1'}
        //                     key={idx} color="blue">{r}</Badge>
        //             </div>
        //         // <Text>{r}</Text>
        //     )
        // );

        WsClient.shared?.subscribe('room', async (data) => {
            console.log(`ListenRooms room ${data?.data}`);
            if (data){
                const rooms: Array<string> = data.data
                setText(
                    rooms.map((r, idx) =>
                            <div className={'m-1 inline'}>
                                <Badge
                                    size={'1'}
                                    key={idx} color="blue">{r}</Badge>
                            </div>
                        // <Text>{r}</Text>
                    )
                );
            }
        }).then(async () => {
            await WsClient?.shared?.send({
                event: "room",
            });
        })

    }, [])

    return <Box width={'100%'} height={'100%'} p={'4'}
        // className={'bg-gray-700'}
        className={
            'shadow-2xs bg-gray-500 rounded-lg'
        }
                m={'5'}
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
                    {/*<Flex direction="column" gap="4">*/}
                    {/*    {...text}*/}
                    {/*</Flex>*/}

                    {...text}

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
                WsClient.shared = new WsClient('ws://8.156.64.230:80/ws/room');
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


