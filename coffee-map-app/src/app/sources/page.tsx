import Link from 'next/link'

export default function Sources() {
    const header_style = {
        "text-decoration" : "underline",
        "padding-top" : "5px",
        "padding-bottom" : "2.5px"
        

    }

    const link_container_style = {
        "display" : "flex",
        "flex-direction" : "column"
    }

    return (
        <div>
            <h2 style={header_style}>Sources List</h2>
            <div>This is a list of data sources and maps used to create maps and fill in data</div>
            <h4 style={header_style}>Ethopia Map Resources</h4>
            <Link href='https://commons.wikimedia.org/wiki/File:Ethiopia_Coffee_Map.png'>Ethopia Coffee Region Wikimedia Map (https://commons.wikimedia.org/wiki/File:Ethiopia_Coffee_Map.png)</Link>
            <h4 style={header_style}>Nepal Map Resources</h4>
            <div style={link_container_style}>
                <Link href="https://github.com/opentechcommunity/map-of-nepal">- Open Tech Community Map Objects (https://github.com/opentechcommunity/map-of-nepal) </Link>
                <Link href="https://nepalitimes.com/caffeine-buzz">- Caffeine Buzz Nepal Coffee Region Map (https://nepalitimes.com/caffeine-buzz)</Link>
            </div>

        </div>
    )
}