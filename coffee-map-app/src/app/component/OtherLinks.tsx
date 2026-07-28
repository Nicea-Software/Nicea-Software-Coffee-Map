'use client'
import { useEffect } from 'react';
import L  from 'leaflet';
import { useMap } from 'react-leaflet';
import { useRouter } from 'next/navigation'

export default function OtherLinks() {
    const map = useMap()
    const router = useRouter()

    useEffect(()=> {
        const other_links = L.control({ position: 'topright'})
        other_links.onAdd = (map) => {
            const other_links_div = L.DomUtil.create('div', 'Links List')
            other_links_div.style.backgroundColor = 'white'
            other_links_div.style.padding = '10px'
            other_links_div.style.color = 'black'

            const title = document.createElement('h4')
            title.textContent = 'Links List';
            other_links_div.appendChild(title)

            const sources_link = document.createElement('div')
            sources_link.textContent = "Sources List"

            sources_link.style.cursor = 'pointer'
            sources_link.style.padding = '4px 0'
            sources_link.style.textDecoration ='underline'

            L.DomEvent.on(sources_link, 'click', () => {
                router.push('sources')
            })

            other_links_div.appendChild(sources_link)

            return other_links_div
        }
        other_links.addTo(map)

        return () => {
            other_links.remove()
        }
    }, [map, router])
    
    return null
}