import SearchForm from '@/components/SearchForm';
import SearchResults from '@/components/SearchResults';
import { SearchParams } from '@/types/search';
import { envConfig } from '@/config/envConfig';

export default async function Page(props: {
  searchParams: Promise<SearchParams>;
}) {
  const searchParams = await props.searchParams
  const query = searchParams.query as string

  const params = new URLSearchParams(
    searchParams as Record<string, string>
  )
  // console.log(params.toString())
  const response = await fetch(`${envConfig.BACKEND_URL}/api/search?${params}`)
  const data = await response.json()
  // console.log(data)

  return (
    <div className="max-w-7xl mx-auto px-4">
      <SearchForm searchParams={searchParams} />
      <SearchResults results={data.results} searchTime={data.time} />
    </div>
  );
}