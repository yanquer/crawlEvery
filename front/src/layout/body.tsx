// @ts-ignore
import {Box, Flex, ScrollArea, Theme, ThemePanel, Text, Heading, Button, Badge, Grid, Table} from "@radix-ui/themes";
import {type ReactNode, useCallback, useEffect, useRef, useState} from "react";
import {WsClient} from "../common/ws_/simple-ws-client";
import {WS_URL} from "../common/defines.ts";
import type {GiftShowTableRow, WsResponse} from "../common/ws_/base.ts";


export const LeftArea = ({
                             areaTitle="运行日志",
                             subEvent="log",
                             show=true,
                         }) => {

    if (!show){
        return <></>
    }

    const [text, setText] = useState<Array<ReactNode>>([]);

    useEffect(() => {

        WsClient.shared?.subscribe(subEvent, async (data) => {
            // console.log(data);
            if (data){
                let text: string = data.data
                if (text.startsWith("=====") && text.includes("@@@")){
                    text = text.split("@@@")[1]
                    text = '"' + text
                }
                setText((lastData) => {
                    lastData.push(
                        <Text as="p" key={lastData.length+1}>
                            {/*[{data.timestamp}]*/}
                            {text}
                        </Text>
                    )
                    // console.log('lastData')
                    // console.log(lastData)
                    return [...lastData];
                });
            }
        }).then()

    }, [])

    return <Box width={'100%'} height={'100%'} p={'4'}
        // className={'bg-gray-800'}
    >
        <Flex width={'100%'} height={'100%'}
              // justify={'center'}
              direction={'column'}
              // className={'bg-gray-800'}
        >
            <Heading size="4" trim="start" mb={'2'}
                     align={'center'}
                     color="gold">
                {areaTitle}
            </Heading>

            <ScrollArea type="always" scrollbars="vertical" style={{ height: '80%' }}>
                <Box p="2" pr="8" width={'85%'}>
                    {/*<Heading size="4" mb="2" trim="start">*/}
                    {/*    Principles of the typographic craft*/}
                    {/*</Heading>*/}
                    {...text}

                </Box>
            </ScrollArea>
        </Flex>
    </Box>
}
export const RightArea = ({show=true}) => {

    return <LeftArea areaTitle={'礼物消息'} subEvent={'gift'} show={show} />;
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

                // m={'5'}
    >
        <Box
            width={'100%'} height={'100%'}
            className={
                'shadow-2xs bg-gray-500 rounded-lg'
            }
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
    </Box>
}


interface ButtonGroupUtilProps {
    parentSetLogRun: (run: boolean)=> any
    parentSetGiftMsgRun: (run: boolean)=> any

}
export const ButtonGroupUtil = (props: ButtonGroupUtilProps) => {

    const [runLog, setRunLog] = useState<boolean>(false);
    const [runGiftMsg, setRunGiftMsg] = useState<boolean>(false);

    return <Box width={'100%'} height={'50px'} p={'4'}
        // className={'bg-gray-800'}
    >

        <Flex width={'100%'} height={'10%'}
            // className={'bg-gray-800'}
            direction={'row'}
              gap={'2'}
        >
            <Button onClick={() => setRunLog(last => {
                const cur = !last
                props.parentSetLogRun(cur)
                return cur
            })} >{runLog ? "关闭运行日志" : "打开运行日志"}</Button>

            <Button onClick={() => setRunGiftMsg(last => {
                const cur = !last
                props.parentSetGiftMsgRun(cur)
                return cur
            })} >{runGiftMsg ? "关闭礼物消息" : "打开礼物消息"}</Button>
        </Flex>
    </Box>
}


interface TableAreaProps {
    areaTitle?: string;
    subEvent?: string;
    show?: boolean;
    wsClient?: WsClient;
}
export const TableArea = ({
                              areaTitle="合计",
                              subEvent="gift",
                              show=true,
                              wsClient=undefined,
                         }: TableAreaProps) => {

    if (!show){
        return <></>
    }

    const [tableData, setTableData] = useState<Array<GiftShowTableRow>>([]);
    const callUpdateTable = useCallback(async (data: WsResponse) => {
        // console.log(data);
        // console.log('callUpdateTable')
        if (data){
            let text: string = data.data

            let tableRows: GiftShowTableRow[] = []

            try {
                tableRows = JSON.parse(text)
            } catch (e) {
                console.error(e)
            }

            if (tableRows && tableRows.length > 0){
                setTableData([...tableRows])
            }

        }
    }, [])

    useEffect(() => {
        console.log(`TableArea wsClient change ${wsClient}`)

        let cancelCall: any = undefined
        const call_ = async () => {
            // while (!wsClient){
            //     await asyncSleep(100)
            // }
            // await asyncSleep(100)

            console.log(`TableArea wsClient change ${wsClient} call_`)
            cancelCall = await wsClient?.subscribe(subEvent, callUpdateTable)
        }

        call_().then()

        return () => cancelCall?.()

    }, [wsClient, show])

    return <Box width={'100%'} height={'100%'} p={'4'}
        // className={'bg-gray-800'}
    >
        <Flex width={'100%'} height={'100%'}
              // justify={'center'}
              direction={'column'}
            // className={'bg-gray-800'}
        >
            <Heading size="4" trim="start" mb={'2'}
                     align={'center'}
                     color="gold">
                {areaTitle}
            </Heading>

            <ScrollArea type="always" scrollbars="vertical" style={{ height: '100%' }}>

                <Table.Root variant="surface">
                    <Table.Header>
                        <Table.Row>
                            <Table.ColumnHeaderCell>轮次/时间</Table.ColumnHeaderCell>
                            <Table.ColumnHeaderCell>直播间号</Table.ColumnHeaderCell>
                            <Table.ColumnHeaderCell>直播间名称</Table.ColumnHeaderCell>
                            <Table.ColumnHeaderCell>本轮环游个数</Table.ColumnHeaderCell>
                            <Table.ColumnHeaderCell>本轮环游数合计</Table.ColumnHeaderCell>
                            <Table.ColumnHeaderCell>上轮环游个数</Table.ColumnHeaderCell>
                            <Table.ColumnHeaderCell>上轮环游数合计</Table.ColumnHeaderCell>
                            <Table.ColumnHeaderCell>环游数增加</Table.ColumnHeaderCell>
                            <Table.ColumnHeaderCell>本轮心动鸭个数</Table.ColumnHeaderCell>
                            <Table.ColumnHeaderCell>本轮心动鸭合计</Table.ColumnHeaderCell>
                            <Table.ColumnHeaderCell>本轮环游 - 心动鸭</Table.ColumnHeaderCell>
                        </Table.Row>
                    </Table.Header>

                    <Table.Body>

                        {
                            tableData.map((row, index) => (
                                <Table.Row key={index}>
                                    <Table.RowHeaderCell>{row.time_round}</Table.RowHeaderCell>
                                    <Table.Cell>{row.room_id}</Table.Cell>
                                    <Table.Cell>{row.room_name}</Table.Cell>
                                    <Table.Cell>{row.word_count}</Table.Cell>
                                    <Table.Cell>{row.word_count_total}</Table.Cell>
                                    <Table.Cell>{row.last_word_count}</Table.Cell>
                                    <Table.Cell>{row.last_word_count_total}</Table.Cell>
                                    <Table.Cell>{row.word_count_sub}</Table.Cell>
                                    <Table.Cell>{row.duck_count}</Table.Cell>
                                    <Table.Cell>{row.duck_count_total}</Table.Cell>
                                    <Table.Cell>{row.world_sub_duck}</Table.Cell>
                                </Table.Row>
                            ))
                        }

                        {/*<Table.Row>*/}
                        {/*    <Table.RowHeaderCell>Danilo Sousa</Table.RowHeaderCell>*/}
                        {/*    <Table.Cell>danilo@example.com</Table.Cell>*/}
                        {/*    <Table.Cell>Developer</Table.Cell>*/}
                        {/*</Table.Row>*/}

                        {/*<Table.Row>*/}
                        {/*    <Table.RowHeaderCell>Zahra Ambessa</Table.RowHeaderCell>*/}
                        {/*    <Table.Cell>zahra@example.com</Table.Cell>*/}
                        {/*    <Table.Cell>Admin</Table.Cell>*/}
                        {/*</Table.Row>*/}

                        {/*<Table.Row>*/}
                        {/*    <Table.RowHeaderCell>Jasper Eriksson</Table.RowHeaderCell>*/}
                        {/*    <Table.Cell>jasper@example.com</Table.Cell>*/}
                        {/*    <Table.Cell>Developer</Table.Cell>*/}
                        {/*</Table.Row>*/}
                    </Table.Body>
                </Table.Root>

            </ScrollArea>


            {/*<ScrollArea type="always" scrollbars="vertical" style={{ height: '80%' }}>*/}
            {/*    <Box p="2" pr="8" width={'85%'}>*/}
            {/*        /!*<Heading size="4" mb="2" trim="start">*!/*/}
            {/*        /!*    Principles of the typographic craft*!/*/}
            {/*        /!*</Heading>*!/*/}
            {/*        {...text}*/}

            {/*    </Box>*/}
            {/*</ScrollArea>*/}
        </Flex>
    </Box>
}

export const Body = () => {

    const clientWs = useRef<WsClient>(undefined)
    const [client, setClient] = useState<WsClient>();

    useEffect(() => {
        console.log('Body useEffect');

        for (let i = 0; i < 3; i++) {
            try {
                // WsClient.shared = new WsClient('http://localhost:8091/ws/room');
                if (!clientWs.current){
                    clientWs.current = new WsClient(WS_URL)
                }
                WsClient.shared = clientWs.current
                setClient(WsClient.shared);
                break;
            } catch (e) {
                console.error(e);
            }
        }

    }, [])

    const [leftShow, setLeftShow] = useState<boolean>(false)
    const [rightShow, setRightShow] = useState<boolean>(false)

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

                {/*<Flex*/}
                {/*    gap={"2"}*/}
                {/*    pb={"4px"}*/}
                {/*    direction={'row'}*/}
                {/*    height={"30%"}*/}
                {/*    width={"100%"}*/}
                {/*    justify={"center"}*/}
                {/*>*/}
                {/*   <Box width={'100%'} height={'100%'}>*/}
                {/*       <Flex*/}
                {/*            justify={'center'}*/}
                {/*            width={'100%'}*/}
                {/*            height={'100%'}*/}
                {/*            direction={'column'}*/}
                {/*       >*/}
                {/*           <ButtonGroupUtil*/}
                {/*               parentSetLogRun={(run_) => setLeftShow(run_)}*/}
                {/*               parentSetGiftMsgRun={(run_) => setRightShow(run_)}*/}
                {/*           />*/}
                {/*       /!*  监听窗口  *!/*/}
                {/*           <ListenRooms />*/}
                {/*       </Flex>*/}
                {/*   </Box>*/}
                {/*</Flex>*/}

                <Flex
                    gap={"2"}
                    pb={"4px"}
                    direction={'row'}
                    height={"100%"}
                    width={"100%"}
                    justify={"center"}
                >
                    <LeftArea show={leftShow} />
                    <TableArea wsClient={client} />
                    <RightArea show={rightShow}/>
                </Flex>
            </Flex>

        </Box>


        {/*<ThemePanel />*/}
    </Theme>
}


