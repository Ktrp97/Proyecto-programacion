
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configurar la página de Streamlit
st.set_page_config(page_title="Chinook Dashboard", layout="wide")


st.title("Dashboard de Análisis de la Base de Datos Chinook")
st.markdown("Chinook con visualizaciones.")

# Conexión a la base de datos
@st.cache_data
def load_data():
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    
    # Consultas y carga de datos
    query_album_tracks = '''
    SELECT Album.Title AS AlbumTitle, COUNT(Track.TrackId) AS TrackCount
    FROM Album 
    JOIN Track ON Album.AlbumId = Track.AlbumId
    GROUP BY Album.AlbumId
    ORDER BY TrackCount DESC
    '''
    
    query_sales_by_genre = '''
    SELECT g.Name AS Genre, SUM(il.UnitPrice * il.Quantity) AS TotalSales
    FROM InvoiceLine il
    JOIN Track t ON il.TrackId = t.TrackId
    JOIN Genre g ON t.GenreId = g.GenreId
    GROUP BY g.Name
    ORDER BY TotalSales DESC
    '''
    
    query_sales_by_customer = '''
    SELECT 
        Customer.FirstName || ' ' || Customer.LastName AS CustomerName, 
        SUM(InvoiceLine.UnitPrice * InvoiceLine.Quantity) AS TotalSales
    FROM 
        Customer
    JOIN 
        Invoice ON Customer.CustomerId = Invoice.CustomerId 
    JOIN 
        InvoiceLine ON Invoice.InvoiceId = InvoiceLine.InvoiceId
    GROUP BY 
        Customer.CustomerId
    ORDER BY 
        TotalSales DESC
    '''
    
    query_sales_by_genre_customer = '''
    SELECT 
        Customer.FirstName || ' ' || Customer.LastName AS CustomerName, 
        Genre.Name AS Genre, 
        SUM(InvoiceLine.UnitPrice * InvoiceLine.Quantity) AS TotalSales
    FROM 
        Customer
    JOIN 
        Invoice ON Customer.CustomerId = Invoice.CustomerId 
    JOIN 
        InvoiceLine ON Invoice.InvoiceId = InvoiceLine.InvoiceId
    JOIN 
        Track ON InvoiceLine.TrackId = Track.TrackId
    JOIN 
        Genre ON Track.GenreId = Genre.GenreId
    GROUP BY 
        Customer.CustomerId, Genre.GenreId
    ORDER BY 
        Customer.CustomerId, TotalSales DESC
    '''
    
    # Ejecutar las consultas y cargar datos en DataFrames
    df_album_tracks = pd.read_sql_query(query_album_tracks, conn)
    df_sales_by_genre = pd.read_sql_query(query_sales_by_genre, conn)
    df_sales_by_customer = pd.read_sql_query(query_sales_by_customer, conn)
    df_sales_by_genre_customer = pd.read_sql_query(query_sales_by_genre_customer, conn)
    
    conn.close()
    
    return df_album_tracks, df_sales_by_genre, df_sales_by_customer, df_sales_by_genre_customer

# Cargar los datos
df_album_tracks, df_sales_by_genre, df_sales_by_customer, df_sales_by_genre_customer = load_data()

# Layout de la aplicación
tab1, tab2, tab3 = st.tabs(["🎵 Álbumes", "🎶 Ventas por Género", "🛍️ Ventas por Cliente y Género"])

# Tab 1: Análisis de Álbumes
with tab1:
    st.subheader("Número de Pistas por Álbum")
    top5_df = df_album_tracks.nlargest(5, 'TrackCount')
    fig1 = go.Figure([go.Bar(x=top5_df['AlbumTitle'], y=top5_df['TrackCount'])])
    fig1.update_layout(
        title='Top 5 Álbumes por Número de Pistas',
        xaxis_title='Título del Álbum',
        yaxis_title='Número de Pistas',
        xaxis_tickangle=-20
    )
    st.plotly_chart(fig1)

# Tab 2: Ventas por Género
with tab2:
    st.subheader("Ventas Totales por Género")
    fig2 = px.bar(df_sales_by_genre, x='Genre', y='TotalSales', title='Ventas Totales por Género')
    st.plotly_chart(fig2)
    st.dataframe(df_sales_by_genre)

# Tab 3: Ventas por Cliente y Género
with tab3:
    st.subheader("Ventas Totales por Cliente y Género")
    heatmap_data = df_sales_by_genre_customer.pivot(index="CustomerName", columns="Genre", values="TotalSales").fillna(0)
    fig3 = px.imshow(
        heatmap_data,
        labels=dict(x="Género", y="Cliente", z="Ventas Totales"),
        color_continuous_scale=["green", "blue"],
        title="Mapa de Calor de Ventas Totales por Cliente y Género"
    )
    st.plotly_chart(fig3)
    st.dataframe(df_sales_by_customer)