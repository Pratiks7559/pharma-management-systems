--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: product_inventory_cache; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.product_inventory_cache (
    product_id bigint NOT NULL,
    total_stock double precision NOT NULL,
    total_batches integer NOT NULL,
    avg_mrp double precision NOT NULL,
    avg_purchase_rate double precision NOT NULL,
    total_stock_value double precision NOT NULL,
    stock_status character varying(50) NOT NULL,
    has_expired_batches boolean NOT NULL,
    last_updated timestamp with time zone NOT NULL
);


ALTER TABLE public.product_inventory_cache OWNER TO postgres;

--
-- Data for Name: product_inventory_cache; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.product_inventory_cache (product_id, total_stock, total_batches, avg_mrp, avg_purchase_rate, total_stock_value, stock_status, has_expired_batches, last_updated) VALUES (11, 20, 1, 20, 12, 400, 'in_stock', false, '2025-12-20 14:39:08.440791+05:30');
INSERT INTO public.product_inventory_cache (product_id, total_stock, total_batches, avg_mrp, avg_purchase_rate, total_stock_value, stock_status, has_expired_batches, last_updated) VALUES (2, 50, 1, 10, 2, 500, 'in_stock', false, '2025-12-20 14:39:13.319128+05:30');
INSERT INTO public.product_inventory_cache (product_id, total_stock, total_batches, avg_mrp, avg_purchase_rate, total_stock_value, stock_status, has_expired_batches, last_updated) VALUES (2755, 20, 1, 30, 15, 600, 'in_stock', false, '2025-12-20 15:12:00.499284+05:30');


--
-- Name: product_inventory_cache product_inventory_cache_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_inventory_cache
    ADD CONSTRAINT product_inventory_cache_pkey PRIMARY KEY (product_id);


--
-- Name: product_inv_has_exp_d4f590_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX product_inv_has_exp_d4f590_idx ON public.product_inventory_cache USING btree (has_expired_batches);


--
-- Name: product_inv_stock_s_f6bd53_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX product_inv_stock_s_f6bd53_idx ON public.product_inventory_cache USING btree (stock_status, total_stock);


--
-- Name: product_inventory_cache_has_expired_batches_fa954e14; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX product_inventory_cache_has_expired_batches_fa954e14 ON public.product_inventory_cache USING btree (has_expired_batches);


--
-- Name: product_inventory_cache_last_updated_faf128d3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX product_inventory_cache_last_updated_faf128d3 ON public.product_inventory_cache USING btree (last_updated);


--
-- Name: product_inventory_cache_stock_status_773e4233; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX product_inventory_cache_stock_status_773e4233 ON public.product_inventory_cache USING btree (stock_status);


--
-- Name: product_inventory_cache_stock_status_773e4233_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX product_inventory_cache_stock_status_773e4233_like ON public.product_inventory_cache USING btree (stock_status varchar_pattern_ops);


--
-- Name: product_inventory_cache_total_stock_557e0697; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX product_inventory_cache_total_stock_557e0697 ON public.product_inventory_cache USING btree (total_stock);


--
-- Name: product_inventory_cache product_inventory_ca_product_id_e7df00d1_fk_core_prod; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_inventory_cache
    ADD CONSTRAINT product_inventory_ca_product_id_e7df00d1_fk_core_prod FOREIGN KEY (product_id) REFERENCES public.core_productmaster(productid) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

